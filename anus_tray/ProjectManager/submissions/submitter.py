import socket
import select
import struct
from functools import reduce
import optparse
import getpass
import datetime
from time import gmtime, strftime, sleep
import sys
import os
import errno


# http class
## ------------------------------------------------------------- ##


class TrHttpRPC(object):
    def __init__(self, host, port=80, logger=None, apphdrs={}):
        self.host = host
        self.port = port
        self.logger = logger
        self.appheaders = apphdrs

        if port <= 0:
            h, c, p = host.partition(":")
            if p:
                self.host = h
                self.port = int(p)

        # embrace and extend errno values
        if not hasattr(errno, "WSAECONNRESET"):
            errno.WSAECONNRESET = 10054
        if not hasattr(errno, "WSAECONNREFUSED"):
            errno.WSAECONNREFUSED = 10061

    def Transaction(
        self, tractorverb, formdata, parseCtxName=None, xheaders={}, analyzer=None
    ):
        """
        Make an HTTP request and retrieve the reply from the server.
        An implementation using a few high-level methods from the
        urllib2 module is also possible, however it is many times
        slower than this implementation, and pulls in modules that
        are not always available (e.g. when running in maya's python).
        """
        outdata = None
        errcode = 0
        s = None

        try:
            # like:  http://tractor-engine:80/Tractor/task?q=nextcmd&...
            t = f"/Tractor/{tractorverb}"

            # we use POST when making changes to the destination (REST)
            req = []
            req.append(f"POST {t} HTTP/1.0")

            for h in self.appheaders:
                req.append(f"{h}: {self.appheaders[h]}")
            for h in xheaders:
                req.append(f"{h}: {xheaders[h]}")

            if formdata:
                fstrip = formdata.decode().strip()
                req.append("Content-Type: application/x-www-form-urlencoded")
                req.append(f"Content-Length: {len(fstrip)}")
                req.append("")  # end of http headers
                req.append(fstrip)

            else:
                req.append("")  # end of http headers

            # error checking?  why be a pessimist?
            # that's why we have exceptions

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host.encode(), self.port))
            s.sendall("\r\n".join(req).encode())

            mustTimeWait = False

            t = ""  # build up the reply text
            while 1:
                r, w, x = select.select([s], [], [], 30)
                if r:
                    if 0 == len(r):
                        self.Debug("time-out waiting for http reply")
                        mustTimeWait = True
                        break
                    else:
                        r = s.recv(4096).decode("utf-8")
                if not r:
                    break
                else:
                    t = f"{t}{r}"

            # Attempt to reduce descriptors held in TIME_WAIT on the
            # engine by dismantling this request socket immediately
            # if we've received an answer.  Usually the close() call
            # returns immediately (no lingering close), but the socket
            # persists in TIME_WAIT in the background for some seconds.
            # Instead, we force it to dismantle early by turning ON
            # linger-on-close() but setting the timeout to zero seconds.
            #
            if not mustTimeWait:
                s.setsockopt(
                    socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0)
                )
            s.close()

            if t and len(t):

                n = t.find("\r\n\r\n")
                h = t[0:n]  # headers

                n += 4

                outdata = t[n:].strip()  # body, or error msg, no CRLF

                n = h.find(" ") + 1
                e = h.find(" ", n)
                errcode = int(h[n:e])

                if errcode == 200:
                    errcode = 0
                    # expecting a json dict?  parse it

                    if outdata and parseCtxName:
                        try:
                            outdata = self.parseJSON(outdata)

                        except Exception:
                            errcode = -1
                            self.Debug(f"json parse:\n {outdata}")
                            outdata = f"parse {parseCtxName}: {self.Xmsg()}"

                if analyzer:
                    analyzer(h)

            else:
                outdata = "no data received"
                errcode = -1

        except Exception as e:
            if e[0] in (errno.ECONNREFUSED, errno.WSAECONNREFUSED):
                outdata = "connection refused"
                errcode = e[0]
            elif e[0] in (errno.ECONNRESET, errno.WSAECONNRESET):
                outdata = "connection dropped"
                errcode = e[0]
            else:
                errcode = -1
                outdata = f"http transaction: {self.Xmsg()}"

        print(errcode)
        print(outdata)
        return (errcode, outdata)

    def parseJSON(self, json):
        #
        # A simpleminded "converter" from inbound json to python dicts.
        #
        # Expect a JSON object, which of course also happens to be the
        # same format as a python dictionary:
        #  { "user": "yoda", "jid": 123, ..., "cmdline": "prman ..." }
        #
        # NOTE: python eval() will *fail* on strings ending in CRLF (\r\n),
        # they must be stripped!  (by our caller, if necessary)
        #
        # We add local variables to stand in for the three JSON
        # "native" types that aren't available in python, however
        # these types aren't expected to appear in tractor data.
        #
        null = None
        true = True
        false = False

        return eval(json)

    def Debug(self, txt):
        if self.logger:
            self.logger.debug(txt)

    def Xmsg(self):
        if self.logger and hasattr(self.logger, "Xcpt"):
            return self.logger.Xcpt()
        else:
            errclass, excobj = sys.exc_info()[:2]
            return f"{errclass.__name__} - {str(excobj)}"


## --------------------------------------------------- ##


def Spool(argv):
    # print(argv)
    """
    tractor-spool - main - examine options, connect to engine, transfer job
    """
    appName = "tractor-spool"
    appVersion = "TRACTOR_VERSION"
    appProductDate = "TRACTOR_BUILD_DATE"
    appDir = os.path.dirname(os.path.realpath(__file__))

    defaultMtd = "S05.local:80"

    spoolhost = socket.gethostname().split(".")[0]  # options can override
    user = getpass.getuser()

    # ------ #
    TrFileRevisionDate = "$DateTime: 2009/04/23 17:17:43 $"
    if not appProductDate[0].isdigit():
        appProductDate = " ".join(TrFileRevisionDate.split()[1:3])
        appVersion = "dev"

    appBuild = "%s %s (%s)" % (appName, appVersion, appProductDate)

    optparser = optparse.OptionParser(
        version=appBuild,
        usage="%prog [options] JOBFILE...\n"
        "%prog [options] --rib RIBFILE...\n"
        "%prog [options] --jdelete JOB_ID",
    )

    optparser.add_option(
        "--priority",
        dest="priority",
        type="float",
        default=1.0,
        help="priority of the new job",
    )

    optparser.add_option(
        "--engine",
        dest="mtdhost",
        type="string",
        default=defaultMtd,
        help="hostname[:port] of the master tractor daemon, "
        "default is '" + defaultMtd + "' - usually a DNS alias",
    )

    optparser.add_option(
        "--hname",
        dest="hname",
        type="string",
        default=spoolhost,
        help="the origin hostname for this job, used to find the "
        "'home blade' that will run 'local' Cmds; default is "
        "the locally-derived hostname",
    )

    optparser.add_option(
        "--user",
        dest="uname",
        type="string",
        default=user,
        help="alternate job owner, default is user spooling the job",
    )

    optparser.add_option(
        "--jobcwd",
        dest="jobcwd",
        type="string",
        default=trAbsPath(os.getcwd()),
        help="blades will attempt to chdir to the specified directory "
        "when launching commands from this job; default is simply "
        "the cwd at time when tractor-spool is run",
    )

    optparser.set_defaults(ribspool=None)
    optparser.add_option(
        "--rib",
        "-r",
        dest="ribspool",
        action="store_const",
        const="rcmd",
        help="treat the flename arguments as RIB files to be rendered; "
        "a single task tractor job is automatically created to handle "
        "the rendering (using prman on remote blade)",
    )

    optparser.add_option(
        "--ribs",
        dest="ribspool",
        action="store_const",
        const="rcmds",
        help="treat the flename arguments as RIB files to be rendered; "
        "a  multi-task tractor job is automatically created to handle "
        "the rendering (using prman on remote blade)",
    )

    optparser.add_option(
        "--nrm",
        dest="ribspool",
        action="store_const",
        const="nrm",
        help="a variant of --rib, above, that causes the generated "
        "tractor job to use netrender on the local blade rather "
        "than direct rendering with prman on a blade; used when "
        "the named RIBfile is not accessible from the remote "
        "blades directly",
    )

    optparser.add_option(
        "--skey",
        dest="ribservice",
        type="string",
        default="pixarRender",
        help="used with --rib to change the service key used to "
        "select matching blades, default: pixarRender",
    )

    optparser.add_option(
        "--jdelete",
        dest="jdel_id",
        type="string",
        default=None,
        help="delete the requested job from the queue",
    )

    optparser.set_defaults(loglevel=1)
    optparser.add_option(
        "-v", action="store_const", const=2, dest="loglevel", help="verbose status"
    )
    optparser.add_option(
        "-q", action="store_const", const=0, dest="loglevel", help="quiet, no status"
    )

    optparser.add_option(
        "--paused",
        dest="paused",
        action="store_true",
        default=False,
        help="submit job in paused mode",
    )

    rc = 0
    xcpt = None

    try:
        options, jobfiles = optparser.parse_args(argv)

        if options.jdel_id:
            if len(jobfiles) > 0:
                optparser.error("too many arguments for jdelete")
                return 1
            else:
                return jobDelete(options)

        if 0 == len(jobfiles):
            optparser.error("no job script specified")
            return 1

        if options.loglevel > 1:
            print(
                "{}\nCopyright (c) 2007-{} Pixar. All rights reserved.".format(
                    appBuild, datetime.datetime.now().year
                )
            )

        if options.mtdhost != defaultMtd:
            h, n, p = options.mtdhost.partition(":")
            if not p:
                options.mtdhost = h + ":80"

        # paused starting is represented by a negative priority
        # decremented by one. This allows a zero priority to pause
        if options.paused:
            try:
                options.priority = str(-float(options.priority) - 1)
            except Exception:
                options.priority = "-2"

        # apply --rib handler by default if all files end in ".rib"
        if not options.ribspool and reduce(
            lambda x, y: x and y, [f.endswith(".rib") for f in jobfiles]
        ):
            options.ribspool = "rcmds"

        #
        # now spool new jobs
        #
        if options.ribspool:
            rc = createRibRenderJob(jobfiles, options)
            if rc == 0:
                rc, xcpt = jobSpool(jobfiles[0], options)
        else:
            for filename in jobfiles:
                rc, xcpt = jobSpool(filename, options)
                if rc:
                    break

    except KeyboardInterrupt:
        xcpt = "received keyboard interrupt"

    except SystemExit as e:
        rc = e

    except:
        errclass, excobj = sys.exc_info()[:2]
        xcpt = f"job spool: {errclass.__name__} - {str(excobj)}"
        rc = 1

    if xcpt:
        print(xcpt, file=sys.stderr)

    """
    write out job id file to source data
    """
    # print(argv)
    # jid_dir = os.path.dirname(argv)
    # jid_path = os.path.join(jid_dir, "job-id-info.json")
    # jid_file = open(jid_path, "w")
    # jid_file.write(xcpt)
    # jid_file.close()

    print("SPOOLED!!")
    return rc


## ------------------------------------------------------------- ##


def trAbsPath(path):
    """
    Generate a canonical path for tractor.  This is an absolute path
    with backslashes flipped forward.  Backslashes have been known to
    cause problems as they flow through system, especially in the
    Safari javascript interpreter.
    """
    return os.path.abspath(path).replace("\\", "/")


## ------------------------------------------------------------- ##


def jobSpool(jobfile, options):
    """
    Transfer the given job (alfred script) to the central job queue.
    """
    # print(jobfile)
    # print(options)

    if options.ribspool:
        alfdata = options.ribjobtxt
    else:
        # usual case, read the alfred jobfile
        f = open(jobfile, "rb")
        alfdata = f.read()
        f.close()

    hdrs = {
        "Content-Type": "application/tractor-spool",
        "X-Tractor-User": options.uname,
        "X-Tractor-Spoolhost": options.hname,
        "X-Tractor-Dir": "/",  # options.jobcwd, HACK
        "X-Tractor-Jobfile": trAbsPath(jobfile),
        "X-Tractor-Priority": str(options.priority),
    }

    return TrHttpRPC(options.mtdhost, 0).Transaction("spool", alfdata, None, hdrs)


## ------------------------------------------------------------- ##