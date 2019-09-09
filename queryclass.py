from flask_restful import Resource, reqparse, request, abort
from flask import jsonify
import sys
import psutil
import cx_Oracle
import json
import json
import time
import config
from jumpssh import SSHSession
from queries import basic_info, system_info, temp_tbs, tbs_detail, default_tbs, space_usage, tbs_quota, fra_status, \
    reco_usage, datafile_usage, rman_time, rman_current, rman_history, log_locations, alert_log_View, locked_obj, \
     asm_usage, asm_stat, mem1, mem2,listener_log,active_instance,statgather


gateway_session = SSHSession('localhost','oracle', password='shadman').open()
remote_session = gateway_session.get_remote_session('localhost','oracle',password='shadman')



con = config.connect()

def get_paginated_list(results, url, start, limit):
    start = int(start)
    limit = int(limit)
    count = len(results)
    if count < start or limit < 0:
        abort(404)
    # make response
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    # make URLs
    # make previous url
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    # make next url
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    return obj





class SetEncoder(json.JSONEncoder):
   def default(self, obj):
        if isinstance(obj, set):
          return list(obj)
          return json.JSONEncoder.default(self, obj)


class Systeminfo(Resource):
       try:
           def get(self):

               gb = 1024 * 1024 * 1024

               while True:
                   usage = json.dumps({



                       # cpuinfo
                       'cpu_percent': psutil.cpu_percent(),
                       'load_avg': psutil.getloadavg(),

                       # memory
                       'memory_total': psutil.virtual_memory().total / gb,
                       'memory_used': psutil.virtual_memory().used / gb,
                       'memory_free': psutil.virtual_memory().free /gb,
                       # swap
                       'swap_total': psutil.swap_memory().total / gb ,
                       'swap_used': psutil.swap_memory().used / gb,
                       'swap_free': psutil.swap_memory().free / gb,

                       # disk
                       'disk_total_u01': psutil.disk_usage('/u01').total / gb,
                       'disk_used_u01': psutil.disk_usage('/u01').used / gb,
                       'disk_free_u01': psutil.disk_usage('/u01').free /gb,



                       'cache_percent': psutil.virtual_memory().cached / psutil.virtual_memory().total * 100,

                   }, cls=SetEncoder)


                   return jsonify('usage:', usage)
                   # return (get_paginated_list(
                   #     usage,
                   #     '/sysinfo',
                   #     start=request.args.get('start', 1),
                   #     limit=request.args.get('limit', 20)))

       except:
             print('system info not parsed sucessfully')




class Basicinfo(Resource):
        try:
            def get(self):
                cursor = con.cursor()
                cursor.execute(basic_info)
                result = cursor.fetchall()
                basiclist = []
                for row in result:
                    basiclist.append({'db_unique_name': row[0], 'log_mode': row[1], 'flashback': row[2],'database_role' : row[3] ,'maxtime': str(row[4])})


                return (get_paginated_list(
                    basiclist,
                    '/baiscinfo',
                    start=request.args.get('start', 1),
                    limit=request.args.get('limit', 20)))

                #return {'basicinfo': basiclist}
                con.close()

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            print(sys.stderr, "Oracle-Error-Code:", error.code)
            print(sys.stderr, "Oracle-Error-Message:", error.message)


class Temptablespace(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(temp_tbs)
            result = cursor.fetchall()
            temptbslist = []
            for row in result:
                temptbslist.append(
                    {'temp_tbs_name': row[0], 'size_in_mb': row[1], 'used_space_mb': row[2], 'free_space_mb': row[3]})


            return (get_paginated_list(
                temptbslist,
                '/temptbslist',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))

            #return {'temptbsspace': temptbslist}
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)



class Tbsdetail(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(tbs_detail)
            result = cursor.fetchall()
            tbslist = []
            for row in result:
                tbslist.append(
                    {'tbs_name': row[0], 'used_mb': row[1], 'free_mb': row[2], 'totalspace': row[3],'pct_free' : row[4]})


            return (get_paginated_list(
                tbslist,
                '/tbslist',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))

            con.close()


            #return {'tbslist': tbslist}

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)



class Defaulttbs(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(default_tbs)
            result = cursor.fetchall()
            defaulttbslist = []
            for row in result:
                defaulttbslist.append(
                    {'USERNAME': row[0], 'DFAULT_TBS': row[1], 'TEMP_TBS': row[2]})


            return (get_paginated_list(
                defaulttbslist,
                '/defaulttbslist',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))

            #return {'defaulttbslist': defaulttbslist}
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)


class Userspaceused(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(space_usage)
            result = cursor.fetchall()
            userspaceused = []
            for row in result:
                userspaceused.append(
                    {'OWNER': row[0], 'TBS_NAME': row[1], 'SIZE_IN_MB': row[2]})


            return (get_paginated_list(
                userspaceused,
                '/userspaceused',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))

            #return {'userspacelist': userspacelist}
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)


class Tbsquota(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(tbs_quota)
            result = cursor.fetchall()
            tbsquota = []
            for row in result:
                tbsquota.append(
                    {'TBS_NAME': row[0], 'USERNAME': row[1], 'SIZE_IN_MB': row[2],'MAX_BYTES': row[3],'MAX_BLOCKS': row[4]})


            return (get_paginated_list(
                tbsquota,
                '/tbsquota',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))

            #return {'tbsquota': tbsquota}
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)



class Frastatus(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(fra_status)
            result = cursor.fetchall()
            fralist = []
            for row in result:
                fralist.append(
                    {'NAME': row[0], 'SPACE_LIMIT_MB': row[1], 'SPACE_USED_MB': row[2],'SPACE_RECLAIM_MB': row[3],'NO_OF_FILE': row[4]})


            return (get_paginated_list(
                fralist,
                '/fralist',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))

            con.close()

            #return {'fralist': fralist}

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)



class Recousage(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(reco_usage)
            result = cursor.fetchall()
            recolist = []
            for row in result:
                recolist.append(
                    {'FILE_TYPE': row[0], 'PERCENT_USED': row[1], 'PERCENT_RECLAIM': row[2], 'NO_OF_FILES': row[3],
                     'CON_ID': row[4]})


            return (get_paginated_list(
                recolist,
                '/recolist',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))

            con.close()

            #return {'recolist': recolist}

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)



class Datafileusage(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(datafile_usage)
            result = cursor.fetchall()
            datafilelist = []
            for row in result:
                datafilelist.append(
                    {'TBS_NAME': row[0], 'DATAFILE': str(row[1]), 'SIZE_MB': row[2], 'MAX_SIZE_MB': row[3]})


            #return {'datafilelist': datafilelist}

            return (get_paginated_list(
                datafilelist,
                '/datafilelist',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))

            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)




class Loginfo(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(log_locations)
            result = cursor.fetchall()
            loginfo = []
            for row in result:
                loginfo.append(
                    {'INST_ID': row[0], 'NAME': str(row[1]), 'VALUE': row[2], 'CON_ID': row[3]})


            #return {'loginfo': loginfo}
            return (get_paginated_list(
                loginfo,
                '/loginfo',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)


class Alertlog(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(alert_log_View)
            result = cursor.fetchall()
            alertlog = []
            for row in result:
                alertlog.append(
                    {'HOST_ID': row[0], 'TIME': str(row[1]), 'MESSAGE': str(row[2])})


            #return {'alertlog': alertlog}
            return (get_paginated_list(
                alertlog,
                '/alertlog',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))

            con.close()


    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)


#rman
class Rmanstartnstop(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(rman_time)
            result = cursor.fetchall()
            rmanstartnstop = []
            for row in result:
                rmanstartnstop.append(
                    {'SESSION_KEY': row[0], 'INPUT_TYPE': str(row[1]), 'STATUS': row[2], 'START_TIME': str(row[3]),'END_TIME': str(row[4]),'HRS': str(row[5])})


            #return {'rmanstartnstop': rmanstartnstop}

            return (get_paginated_list(
                rmanstartnstop,
                '/rmanstartnstop',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)



class Rmanrunning(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(rman_current)
            result = cursor.fetchall()
            rmanrunning = []
            for row in result:
                rmanrunning.append(
                    {'SID': row[0], 'SERIAL#' : row[1], 'CONTEXT': str(row[2]), 'SO_FAR': str(row[3]),'TOTALWORK': str(row[4]), 'COMPLETE': str(row[5])})


            #return {'rmanrunning': rmanrunning}

            return (get_paginated_list(
                rmanrunning,
                '/rmanrunning',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)


class Rmanhistory(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(rman_history)
            result = cursor.fetchall()
            rmanhist = []
            for row in result:
                rmanhist.append(
                    {'SESSION_KEY': row[0], 'INPUT_TYPE': str(row[1]), 'STATUS': str(row[2]), 'START_TIME': str(row[3]),
                     'END_TIME': str(row[4]), 'HRS': str(row[5])})


            #return {'rmanhist': rmanhist}
            return (get_paginated_list(
                rmanhist,
                '/rmanhist',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)



#



class Listenerlog(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(listener_log)
            result = cursor.fetchall()
            listenerlog = []
            for row in result:
                listenerlog.append(
                    {'LOGTIME': str(row[0]), 'CONNECT': str(row[1]), 'PROTOCOL': str(row[2]), 'ACTION': str(row[3]),
                     'SERVICE': str(row[4])})


            #return {'listenerlog': listenerlog}

            return (get_paginated_list(
                listenerlog,
                '/listenerlog',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()



    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)


class Lockedobj(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(locked_obj)
            result = cursor.fetchall()
            lockedobj = []
            for row in result:
                lockedobj.append(
                    {'OWNER': str(row[0]), 'OBJ_NAME': str(row[1]), 'OBJ_TYPE': str(row[2]), 'SID': str(row[3]),
                     'SERIAL#': str(row[4]),'STATUS': str(row[5]),'OSUSER': str(row[6]),'MACHINE': str(row[7])})


            #return {'lockedobj': lockedobj}

            return (get_paginated_list(
                lockedobj,
                '/lockedobj',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)




class Pgainfo(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(mem1)
            result = cursor.fetchall()
            pgainfo = []
            for row in result:
                pgainfo.append(
                    {'LOGON': str(row[0]), 'SID': str(row[1]), 'SERIAL#': str(row[2]), 'PGA_MB_USED': str(row[3]),
                     'USERNAME': str(row[4]),'STATUS': str(row[5]),'OSUSER': str(row[6]),'MACHINE': str(row[7]),'PROGRAM': str(row[8]),'MODULE': str(row[9])})


            #return {'pgainfo': pgainfo}

            return (get_paginated_list(
                pgainfo,
                '/pgainfo',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)



class Asmdiskinfo(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(asm_usage)
            result = cursor.fetchall()
            asmdiskinfo = []
            for row in result:
                asmdiskinfo.append(
                    {'GROUP_NAME': str(row[0]), 'SECTOR_SIZE': str(row[1]), 'BLOCK_SIZE': str(row[2]), 'AU_SIZE': str(row[3]),
                     'STATE': str(row[4]),'TYPE': str(row[5]),'TOTAL_MB': str(row[6]),'USED_MB': str(row[7]),'PCT_USED': str(row[8])})


            #return {'asmdiskinfo': asmdiskinfo}
            return (get_paginated_list(
                asmdiskinfo,
                '/asmdiskinfo',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)


class Asmstatinfo(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(asm_stat)
            result = cursor.fetchall()
            asmstatinfo = []
            for row in result:
                asmstatinfo.append(
                    {'DISK_GROUP_NAME': str(row[0]), 'DISK_PATH': str(row[1]), 'READS': str(row[2]), 'WRITES': str(row[3]),
                     'READ_ERR': str(row[4]),'WRITE_ERR': str(row[5]),'READ_TIME': str(row[6]),'WRITE_TIME': str(row[7]),'BYTES_READ': str(row[8]),'BYTES_WRITTEN': str(row[8])})


            #return {'asmstatinfo': asmstatinfo}

            return (get_paginated_list(
                asmstatinfo,
                '/asmstatinfo',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)




class Sshconnectivity(Resource):
    try:
        def get(self):
            if remote_session.exists('/home/oracle/.bashrc'):
             return{'info' : 'Connection establishment successful'}
    except Exception as e:
        error, = e.args
        print(error)



class Racinstance(Resource):
    try:
        def get(self):
            cursor = con.cursor()
            cursor.execute(active_instance)
            result = cursor.fetchall()
            activeinstance = []
            for row in result:
                activeinstance.append(
                    {'INST_NUM)': str(row[0]), 'INST_NAME': str(row[1]), 'CON_ID': str(row[2])})


            #return {'asmstatinfo': asmstatinfo}

            return (get_paginated_list(
                activeinstance,
                '/activeinstance',
                start=request.args.get('start', 1),
                limit=request.args.get('limit', 20)))
            con.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(sys.stderr, "Oracle-Error-Code:", error.code)
        print(sys.stderr, "Oracle-Error-Message:", error.message)


class Statgather(Resource):
    try :
        def post(self):

            cursor = con.cursor()
            cursor.execute(statgather['schemastatgather'])
            result = con.commit()
            return ("PL/SQL successful executed ...")
            con.close()

    except cx_Oracle.DatabaseError as e:
        err, = e.args
        print("\n".join([str(err.code), err.message, err.context]))