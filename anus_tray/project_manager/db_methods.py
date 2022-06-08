import sqlite3
import os
from sqlite3.dbapi2 import Error
from Utils.makers import *
from errno import errorcode
import marshal
import sys
import json
import gazu

"""
future kitsu integration:

gazu.client.set_host("https://zou.animation-luzern.ch")
gazu.log_in("fucker@email.com","password")
all_projects = gazu.project.all_projects()
open_projects = gazu.project.all_open_projects()

for project in open_projects:
    project_name = p["name"]
    project_id = p["id"]

    sequences_proj = gazu.shot.all_sequences_for_project(project["id"])
    shots = gazu.shot.all_shots_for_project(project)

    for s in shots:
        shot = gazu.shot.get_shot(s["id"])
        sequence = gazu.shot.get_sequence(s["id"])

    print(p["name"])

#p are all current open projects



"""


class ProjectInfoHandling:
    @staticmethod
    def get_project():
        # home = os.path.expanduser("~")
        # history_file = os.path.join(home, ".active_hslu_project", "project_history.txt")

        history_file = os.getenv("ANUS_PROJECT_MEMORY")
        print(history_file)
        try:
            if os.path.exists(history_file):

                with open(history_file, "r") as f:
                    # first line of f
                    db_path = f.readline().strip()
                    # return db_path
                    print("db_path: ", db_path)

                if os.path.exists(db_path):
                    print(f"{db_path} exists")
                    return db_path

                else:
                    print(
                        f"WARNING: database path is '{db_path}' and does not exist or can't be read"
                    )
                    db_path = None
                    return db_path

        except Exception as e:
            print(e)
            print(f"WARNING: History File: '{history_file}' does not exist")
            db_path = None
            return db_path

    @staticmethod
    def set_project_file_history( projectpath):
        """
        Store the information of the currently saved or loaded project in a file
        """
        path_to_store_info = os.path.dirname(os.getenv("ANUS_PROJECT_MEMORY"))

        if os.path.exists(path_to_store_info):
            shutil.rmtree(path_to_store_info)

        CreationMethods.makedir(path_to_store_info)
        file_to_store = os.getenv("ANUS_PROJECT_MEMORY")
        with open(file_to_store, "w") as f:
            f.write(f"{projectpath}")

        return file_to_store


def connection_check(method):
    def wrapper(self, *args, **kwargs):
        # query shots into tables with foreign keys
        self.LoadDB(self.db_path)
        try:
            method(self, *args, **kwargs)
        except Exception as e:
            print(e)
            raise
        finally:
            if self.conn:
                self.conn.close()

    return wrapper


def connection_result(method):
    def wrapper(self, *args, **kwargs):
        # query shots into tables with foreign keys
        self.LoadDB(self.db_path)
        try:
            res = method(self, *args, **kwargs)
            return res
        except Exception as e:
            print("Error: ", e)
            return None
        finally:
            if self.conn:
                self.conn.close()

    return wrapper


class MethodsDB:
    def __init__(self):
        self.sequence_schema = """CREATE TABLE IF NOT EXISTS sequences 
                                ( sequence_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, sequencename text)"""
        self.shot_schema = """CREATE TABLE IF NOT EXISTS shots
                                ( shot_id INTEGER UNIQUE NOT NULL, shotname text, sequence_id INTEGER, PRIMARY KEY(shot_id), FOREIGN KEY(sequence_id) REFERENCES sequences(sequence_id) )"""
        self.job_schema = """CREATE TABLE IF NOT EXISTS jobs
                                ( job_id INTEGER UNIQUE NOT NULL , job_uuid text ,jobname text, shot_id INTEGER, PRIMARY KEY(job_id), FOREIGN KEY(shot_id) REFERENCES shots(shot_id) )"""
        self.job_history_schema = """CREATE TABLE IF NOT EXISTS job_history
                                ( job_history_id INTEGER UNIQUE NOT NULL ,job_uuid text ,job_name text ,jobfile_path text, jobfile_type text, jobfile_sent INTEGER, jobfile_cooked INTEGER, PRIMARY KEY(job_history_id) )"""
        self.task_schema = """CREATE TABLE IF NOT EXISTS tasks
                                ( task_id INTEGER UNIQUE NOT NULL, properties blob, job_id INTEGER, PRIMARY KEY(task_id), FOREIGN KEY(job_id) REFERENCES jobs(job_id) )"""
        self.db_path = ProjectInfoHandling.get_project()
        if self.db_path:
            self.conn = self.ConnectionToDB()
            self.cur = self.conn.cursor()
        else:
            self.conn = None
            self.cur = None

    """
    Establish Elements
    """

    def CheckConn(self):
        if self.cur:
            return True
        else:
            return False

    def CloseConnection(self):
        try:
            self.conn.close()
            print("Connection closed")
        except Exception as e:
            print(e)
            pass

    def ConnectionToDB(self):
        con = sqlite3.connect(self.db_path)

        return con

    def CreateDB(self, filepath):

        self.LoadDB(filepath)
        try:
            self.QueryTableSchema(self.sequence_schema)
            self.QueryTableSchema(self.shot_schema)
            self.QueryTableSchema(self.job_schema)
            self.QueryTableSchema(self.job_history_schema)
            self.QueryTableSchema(self.task_schema)

        except Exception as e:
            print(e)
            print(self.db_path)

    def LoadDB(self, filepath):
        # load db
        self.CloseConnection()

        self.db_path = filepath
        self.conn = self.ConnectionToDB()
        self.cur = self.conn.cursor()

    """
    Query Tables
    """

    @connection_check
    def QueryTableSchema(self, schema):
        self.cur.execute(schema)
        self.conn.commit()
        self.cur.close()

    """
    Insert Elements
    """

    @connection_check
    def InsertSequenceDB(self, sequence_info):
        # sequence_info should be a tuple list of the things
        self.cur.execute(
            """INSERT INTO sequences
                    (sequence_id, sequencename) VALUES(?,?)""",
            sequence_info,
        )
        self.conn.commit()
        self.cur.close()

    @connection_check
    def InsertShotDB(self, shot_info):
        # shot_info should be a tuple list of the things
        self.cur.execute(
            """INSERT INTO shots
                    (shot_id, shotname, sequence_id) VALUES(?,?,?)""",
            shot_info,
        )
        self.conn.commit()
        self.cur.close()

    @connection_check
    def InsertJobDB(self, job_info):
        # job_info should be a tuple list of the things
        self.cur.execute(
            """INSERT INTO jobs
                    (job_id, job_uuid, jobname, shot_id) VALUES(?,?,?,?)""",
            job_info,
        )
        self.conn.commit()
        self.cur.close()

    @connection_check
    def InsertJobHistoryDB(self, job_history_info):
        self.cur.execute(
            """INSERT INTO job_history
                    (job_history_id, job_uuid, job_name, jobfile_path, jobfile_type, jobfile_cooked, jobfile_sent) VALUES(?,?,?,?,?,?,?)""",
            job_history_info,
        )
        self.conn.commit()
        self.cur.close()

    """
    Get Max Element IDs
    """

    @connection_result
    def GetSequenceMaxId(self):
        # select the last number in the row
        self.cur.execute("""SELECT MAX(sequence_id) FROM sequences""")
        max_id = self.cur.fetchone()[0]
        self.cur.close()
        if max_id:
            return max_id
        else:
            return None

    @connection_result
    def GetShotMaxId(self):
        # select the last number in the row
        self.cur.execute("""SELECT MAX(shot_id) FROM shots""")
        max_id = self.cur.fetchone()[0]
        self.cur.close()
        if max_id:
            return max_id
        else:
            return None

    @connection_result
    def GetJobMaxId(self):
        # select the last number in the row
        self.cur.execute("""SELECT MAX(job_id) FROM jobs""")
        max_id = self.cur.fetchone()[0]
        self.cur.close()
        if max_id:
            return max_id
        else:
            return None

    @connection_result
    def GetJobHistoryMaxId(self):
        # select the last number in the row
        self.cur.execute("""SELECT MAX(job_history_id) FROM job_history""")
        max_id = self.cur.fetchone()[0]
        self.cur.close()
        if max_id:
            return max_id
        else:
            return None

    """
    Remove Elements
    """

    @connection_check
    def RemoveSequenceFromDB(self, seq_id):
        """
        First we delete the sequence by id
        """
        # self.cur.execute("""DELETE FROM shots WHERE sequence_id=?""", (seq_id,))
        # self.RemoveShotGroupFromDB(seq_id)
        # self.LoadDB(self.db_path)
        self.cur.execute("""DELETE FROM sequences WHERE sequence_id=?""", (seq_id,))

        self.conn.commit()
        self.cur.close()

    @connection_check
    def RemoveShotGroupFromDB(self, sequence_id):
        # remove column
        """
        First we delete the shot by id
        """
        self.cur.execute("""DELETE FROM shots WHERE sequence_id=?""", (sequence_id,))
        self.conn.commit()
        self.cur.close()

    @connection_check
    def RemoveShotFromDB(self, shot_id):
        """
        First we delete the shot by id
        """
        self.cur.execute("""DELETE FROM shots WHERE shot_id=?""", (shot_id,))
        self.conn.commit()
        self.cur.close()

    @connection_check
    def RemoveJobFromDB(self, job_id):
        self.cur.execute("""DELETE FROM jobs WHERE job_id=?""", (job_id,))
        self.conn.commit()
        self.cur.close()

    @connection_check
    def RemoveJobGroupFromDB(self, shot_id):
        # remove column
        """
        First we delete the shot by id
        """
        self.cur.execute("""DELETE FROM jobs WHERE shot_id=?""", (shot_id,))
        self.conn.commit()
        self.cur.close()

    @connection_check
    def RemoveJobHistoryByUUID(self, uuid):
        self.cur.execute("""DELETE FROM job_history WHERE job_uuid=?""", (uuid,))
        self.conn.commit()
        self.cur.close()

    """
    Retrieve Elements
    """

    @connection_result
    def FetchAllSequences(self):
        self.cur.execute("""SELECT * FROM sequences""")
        sequences = self.cur.fetchall()
        self.cur.close()
        return sequences

    @connection_result
    def FetchAllShots(self):
        self.cur.execute("""SELECT * FROM shots""")
        shots = self.cur.fetchall()
        self.cur.close()
        return shots

    @connection_result
    def FetchAllShotsBySequence(self, sequence_id):
        self.cur.execute("""SELECT * FROM shots WHERE sequence_id=?""", (sequence_id,))
        shots = self.cur.fetchall()
        self.cur.close()
        return shots

    @connection_result
    def FetchAllJobs(self):
        self.cur.execute("""SELECT * FROM jobs""")
        jobs = self.cur.fetchall()
        self.cur.close()
        return jobs

    @connection_result
    def FetchAllJobsByShot(self, shot_id):
        # fetch sequence info from db
        self.cur.execute("""SELECT * FROM jobs WHERE shot_id=?""", (shot_id,))
        jobs = self.cur.fetchall()
        self.cur.close()
        return jobs

    @connection_result
    def FetchAllJobsByUUID(self, uuid):
        self.cur.execute("""SELECT * FROM jobs WHERE job_uuid=?""", (uuid,))
        jobs = self.cur.fetchall()
        self.cur.close()
        return jobs

    @connection_result
    def FetchAllJobHistory(self):
        self.cur.execute("""SELECT * FROM job_history""")
        jobs = self.cur.fetchall()
        self.cur.close()
        return jobs

    @connection_result
    def FetchAllJobHistoryByUUID(self, uuid):
        # fetch all jobs that have a specific uuid
        self.cur.execute("""SELECT * FROM job_history WHERE job_uuid=?""", (uuid,))
        jobs = self.cur.fetchall()
        self.cur.close()
        return jobs

    """
    Element Update
    """

    @connection_check
    def ChangeJobHistoryNameByUUID(self, jobname, uuid):
        self.cur.execute(
            """UPDATE job_history SET job_name=? WHERE job_uuid=?""", (jobname, uuid)
        )
        print("Job Name in History Changed ")
        self.conn.commit()
        self.cur.close()

    @connection_check
    def ChangeJobCookedByUUID(self, bool, uuid):
        self.cur.execute(
            """UPDATE job_history SET jobfile_cooked=? WHERE job_uuid=?""", (bool, uuid)
        )
        print("Job has been cooked !")
        self.conn.commit()
        self.cur.close()

    @connection_check
    def ChangeJobNameByUUID(self, jobname, uuid):
        self.cur.execute(
            """UPDATE jobs SET jobname=? WHERE job_uuid=?""", (jobname, uuid)
        )
        print("Job Name per Shot Changed ")
        self.conn.commit()
        self.cur.close()

