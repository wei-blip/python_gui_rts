import sqlite3

class sqlite_db():

    def __init__(self, db_location):
        try:
            self.__connection = sqlite3.connect(db_location)
            self.__cursor = self.__connection.cursor()
        except sqlite3.Error as e:
            print(f"Error while connect to {db_location}")
            print(e)

    def __del__(self):
        try:
            self.__connection.close()
        except sqlite3.Error as e:
            print(e)

    def create_tables(self):
        sql_create_table_main = """CREATE TABLE IF NOT EXISTS main
                        ( tm              DATETIME NOT NULL, 
                            sn              TEXT NOT NULL,
                            uut_dev_eui     TEXT NOT NULL,
                            uut_join_key    TEXT NOT NULL,
                            dev_type        TEXT NOT NULL,
                            last_fw_ver     TEXT NOT NULL,
                            hw_ver          INTEGER,
                            PRIMARY KEY (sn)
                        )"""
        sql_create_table_meas = """CREATE TABLE IF NOT EXISTS meas(
                            main_sn     TEXT NOT NULL,
                            record_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                            tm          DATETIME NOT NULL, 
                            ref_sn      TEXT,       ref_dev_eui TEXT NOT NULL,                    
                            fei         REAL,       snr         REAL,       per         REAL,       rssi        REAL,
                            pwr         REAL,
                            ref_ds_t    REAL,       uut_ds_t    REAL,
                            ref_vcc     REAL,       uut_vcc     REAL,
                            ref_adc_t   REAL,       uut_adc_t   REAL,
                            ref_acc_x   REAL,       uut_acc_x   REAL,
                            ref_acc_y   REAL,       uut_acc_y   REAL,
                            ref_acc_z   REAL,       uut_acc_z   REAL,
                            ref_vibro_x REAL,       uut_vibro_x REAL,
                            ref_vibro_y REAL,       uut_vibro_y REAL,
                            ref_vibro_z REAL,       uut_vibro_z REAL,
                            uut_cur_min REAL,       
                            uut_cur_avg REAL,
                            uut_cur_max REAL,
                            fw_ver      INTEGER,
                            FOREIGN KEY (main_sn) REFERENCES main (sn)
                            )"""
        sql_create_table_comment = """CREATE TABLE IF NOT EXISTS comment (
                            tm          DATETIME NOT NULL,
                            comment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                            main_sn     TEXT NOT NULL,
                            meas_id     INTEGER,
                            comment_txt TXT,
                            FOREIGN KEY (main_sn) REFERENCES main (sn)
                            )"""
        sql_create_table_lifecycle = """CREATE TABLE IF NOT EXISTS lifecycle (
                            main_sn     TEXT NOT NULL,
                            record_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                            tm          DATETIME NOT NULL,
                            status      TEXT,
                            user_id     TEXT,
                            lf_fw_ver   INTEGER,
                            status_fw   TEXT,
                            FOREIGN KEY (main_sn) REFERENCES main (sn)
                            )"""
        try:
            self.__cursor.execute(sql_create_table_main)
        except sqlite3.Error as e:
            print("Error in sql_create_table_main request")
            print(e)
        try:
            self.__cursor.execute(sql_create_table_meas)
        except sqlite3.Error as e:
            print("Error in sql_create_table_meas request")
            print(e)
        try:
            self.__cursor.execute(sql_create_table_comment)
        except sqlite3.Error as e:
            print("Error in sql_create_table_main comment")
            print(e)
        try:
            self.__cursor.execute(sql_create_table_lifecycle)
        except sqlite3.Error as e:
            print("Error in sql_create_table_lifecycle request")
            print(e)
        self.__connection.commit()

    def drop_all_tables(self):
        try:
            self.__cursor.execute("DROP TABLE IF EXISTS main")
        except sqlite3.Error as e:
            print(f"Error delete table main")
            print(e)
        try:        
            self.__cursor.execute("DROP TABLE IF EXISTS meas")
        except sqlite3.Error as e:
            print(f"Error delete table main")
            print(e)
        try:        
            self.__cursor.execute("DROP TABLE IF EXISTS comment")
        except sqlite3.Error as e:
            print(f"Error delete table meas")
            print(e)
        try:                    
            self.__cursor.execute("DROP TABLE IF EXISTS lifecycle")
        except sqlite3.Error as e:
            print(f"Error delete table lifecycle")
            print(e)

    def sn_in_bd(self, sn):
        sql = f"SELECT count(sn) FROM main WHERE sn = '{sn}'"
        # print(sql)
        self.__cursor.execute(sql)
        tmp = self.__cursor.fetchall()[0][0]
        if  tmp > 0:
            return True
        else:
            return False

    def put_data_into_db(self, data):
        if not self.sn_in_bd(data['uut']['sn']):
            self.__cursor.execute("INSERT INTO main(tm, sn, uut_dev_eui, uut_join_key, dev_type, last_fw_ver, hw_ver) VALUES (DATETIME('now'), :sn, :uut_dev_eui, :uut_join_key, :dev_type, :last_fw_ver, :hw_ver)",
                                  { 'sn':           data['uut']['sn'],
                                    'uut_dev_eui':  data['uut']['dev_eui'],
                                    'uut_join_key': data['uut']['join_key'],
                                    'dev_type':     data['uut']['dev_type'],
                                    'last_fw_ver':  data['uut']['fw_ver'],
                                    'hw_ver':       1})
        self.__cursor.execute("""INSERT INTO meas(tm,  main_sn,  ref_dev_eui,  ref_sn,  fei,  snr,  per,  rssi,  pwr,  ref_ds_t,  uut_ds_t,  ref_vcc,  uut_vcc,  ref_adc_t,  uut_adc_t,  ref_acc_x,  uut_acc_x,  ref_acc_y,  uut_acc_y,  ref_acc_z,  uut_acc_z,  ref_vibro_x,  uut_vibro_x,  ref_vibro_y,  uut_vibro_y,  ref_vibro_z,  uut_vibro_z,  fw_ver) VALUES
                                    (DATETIME('now'), :main_sn, :ref_dev_eui, :ref_sn, :fei, :snr, :per, :rssi, :pwr, :ref_ds_t, :uut_ds_t, :ref_vcc, :uut_vcc, :ref_adc_t, :uut_adc_t, :ref_acc_x, :uut_acc_x, :ref_acc_y, :uut_acc_y, :ref_acc_z, :uut_acc_z, :ref_vibro_x, :uut_vibro_x, :ref_vibro_y, :uut_vibro_y, :ref_vibro_z, :uut_vibro_z, :fw_ver)""",
                              {'main_sn':       data['uut']['sn'],
                               'ref_dev_eui':   data['ref']['dev_eui'],
                               'ref_sn':        data['ref']['sn'],
                               'fei':           data['uut']['fei'],
                               'snr':           data['uut']['snr'],
                               'per':           data['uut']['per'],
                               'rssi':          data['uut']['rssi'],
                               'pwr':           data['uut']['pwr_meas'],
                               'ref_ds_t':      data['ref']['ds18b20_t'],
                               'uut_ds_t':      data['uut']['ds18b20_t'],
                               'ref_vcc':       data['ref']['vcc'],
                               'uut_vcc':       data['uut']['vcc'],
                               'ref_adc_t':     data['ref']['adc_t'],
                               'uut_adc_t':     data['uut']['adc_t'],
                               'ref_acc_x':     data['ref']['acc_x'],
                               'ref_acc_y':     data['ref']['acc_y'],
                               'ref_acc_z':     data['ref']['acc_z'],
                               'uut_acc_x':     data['uut']['acc_x'],
                               'uut_acc_y':     data['uut']['acc_y'],
                               'uut_acc_z':     data['uut']['acc_z'],
                               'ref_vibro_x':   data['ref']['vibro_x'],
                               'ref_vibro_y':   data['ref']['vibro_y'],
                               'ref_vibro_z':   data['ref']['vibro_z'],
                               'uut_vibro_x':   data['uut']['vibro_x'],
                               'uut_vibro_y':   data['uut']['vibro_y'],
                               'uut_vibro_z':   data['uut']['vibro_z'],
                               'fw_ver':        data['uut']['fw_ver']})
        self.__connection.commit()


if __name__ == "__main__":

    db = sqlite_db('rts.sq')
    # db.drop_all_tables()
    db.create_tables()
    print(db.sn_in_bd('123456789'))


    


# select_req='''SELECT main.sn, main.uut_dev_eui, meas.tm FROM meas INNER JOIN main ON  meas.main_sn = main.sn'''
#
# cursor.execute(select_req)
# cursor.fetchall()
#
# column_names = [description[0] for description in cursor.description]
# print(column_names)
#
# bd.commit()