import psutil




# dsn_tns = cx_Oracle.makedsn('localhost', 1521, 'shadman')
# con = cx_Oracle.connect("shadman", "shadman", dsn_tns)

#if would like to logged in as sysdba use the following parameters
# con = cx_Oracle.connect("sys", "tigerit", dsn_tns,mode=cx_Oracle.SYSDBA)





#queries
basic_info = "select a.DB_UNIQUE_NAME, a.LOG_MODE, a.FLASHBACK_ON, a.DATABASE_ROLE, floor(sysdate - startup_time) || ' day(s) ' || trunc( 24*((sysdate-startup_time) - trunc(sysdate-startup_time))) || ' hour(s) ' || mod(trunc(1440*((sysdate-startup_time) - trunc(sysdate-startup_time))), 60) ||' minute(s) ' || mod(trunc(86400*((sysdate-startup_time) - trunc(sysdate-startup_time))), 60) ||' seconds' uptime from v$database a, v$instance b "
system_info = """select distinct
   stat_name   c1,
   value       c2
from
   dba_hist_osstat
where
   stat_name in (
   'NUM_CPU_CORES',
   'NUM_CPU_SOCKETS',
   'PHYSICAL_MEMORY_BYTES'
)"""


temp_tbs = "select TABLESPACE_NAME,tablespace_size/1024/1024 as size_in_MB, allocated_space/1024/1024 as used_space_in_MB,free_space/1024/1024 as free_space_in_MB from DBA_TEMP_FREE_SPACE "
tbs_detail = "select fs.tablespace_name,(df.totalspace - fs.freespace) ,fs.freespace ,df.totalspace,round(100 * (fs.freespace / df.totalspace))  from (select tablespace_name,round(sum(bytes) / 1048576) TotalSpace from dba_data_files group by tablespace_name) df,(select tablespace_name,round(sum(bytes) / 1048576) FreeSpace from dba_free_space group by tablespace_name) fs where df.tablespace_name = fs.tablespace_name"
default_tbs = "select USERNAME,DEFAULT_TABLESPACE,TEMPORARY_TABLESPACE from dba_users where default_tablespace not in ('SYSTEM','SYSAUX')"
space_usage = "select owner,TABLESPACE_NAME,sum(bytes)/1024/1024 size_in_mb from dba_segments group by owner,TABLESPACE_NAME"
tbs_quota = "select tablespace_name,username,bytes/1024/1024,max_bytes,max_blocks from DBA_TS_QUOTAS"


fra_status = "SELECT name,space_limit/1024/1024 as space_limit_mb,space_used/1024/1024 as space_used_mb,space_reclaimable/1024/1024 as space_reclaimable_mb,number_of_files  FROM V$RECOVERY_FILE_DEST"
reco_usage = "SELECT * FROM V$RECOVERY_AREA_USAGE"
datafile_usage = " select tablespace_name,file_name as datafile, bytes/1024/1024 as size_in_MB,maxbytes/1024/1024 as max_size_mb from dba_data_files"

rman_time = "select SESSION_KEY, INPUT_TYPE, STATUS,to_char(START_TIME,'mm/dd/yy hh24:mi') start_time,to_char(END_TIME,'mm/dd/yy hh24:mi') end_time,elapsed_seconds/3600 hrs from V$RMAN_BACKUP_JOB_DETAILS order by session_key"
rman_current = """SELECT SID, SERIAL#, CONTEXT, SOFAR, TOTALWORK,ROUND (SOFAR/TOTALWORK*100, 2) "% COMPLETE" FROM V$SESSION_LONGOPS WHERE OPNAME LIKE 'RMAN%' AND OPNAME NOT LIKE '%aggregate%' AND TOTALWORK! = 0 AND SOFAR <> TOTALWORK"""
rman_history = "select SESSION_KEY, INPUT_TYPE, STATUS,to_char(START_TIME,'mm-dd-yyyy hh24:mi:ss') as RMAN_Bkup_start_time,to_char(END_TIME,'mm-dd-yyyy hh24:mi:ss') as RMAN_Bkup_end_time,elapsed_seconds/3600 Hours from V$RMAN_BACKUP_JOB_DETAILS order by session_key"


log_locations = """select * from v$diag_info"""
alert_log_View = """SELECT host_id,record_id,error_instance_id,error_instance_sequence,to_char(originating_timestamp,'DD.MM.YYYY HH24:MI:SS'),message_text FROM v$alert_log"""



locked_obj = """

select
   c.owner,
   c.object_name,
   c.object_type,
   b.sid,
   b.serial#,
   b.status,
   b.osuser,
   b.machine
from
   v$locked_object a ,
   v$session b,
   dba_objects c
where
   b.sid = a.session_id
and
   a.object_id = c.object_id;


"""

asm_usage = """SELECT
    name                                     group_name
  , sector_size                              sector_size
  , block_size                               block_size
  , allocation_unit_size                     allocation_unit_size
  , state                                    state
  , type                                     type
  , total_mb                                 total_mb
  , (total_mb - free_mb)                     used_mb
  , ROUND((1- (free_mb / total_mb))*100, 2)  pct_used
FROM
    v$asm_diskgroup
ORDER BY
    name"""


asm_stat =  """SELECT
    a.name                disk_group_name
  , b.path                disk_path
  , b.reads               reads
  , b.writes              writes
  , b.read_errs           read_errs
  , b.write_errs          write_errs
  , b.read_time           read_time
  , b.write_time          write_time
  , b.bytes_read/1024/1024/1024         bytes_read
  , b.bytes_written/1024/1024/1024       bytes_written
FROM
    v$asm_diskgroup a JOIN v$asm_disk b USING (group_number)
ORDER BY
    a.name"""





mem1 = """SELECT DECODE(TRUNC(SYSDATE - LOGON_TIME), 0, NULL, TRUNC(SYSDATE - LOGON_TIME) || ' Days' || ' + ') ||
    TO_CHAR(TO_DATE(TRUNC(MOD(SYSDATE-LOGON_TIME,1) * 86400), 'SSSSS'), 'HH24:MI:SS') LOGON,
    SID, v$session.SERIAL#, v$process.SPID , ROUND(v$process.pga_used_mem/(1024*1024), 2) PGA_MB_USED,
    v$session.USERNAME, STATUS, OSUSER, MACHINE, v$session.PROGRAM, MODULE
    FROM v$session, v$process
    WHERE v$session.paddr = v$process.addr
    and status = 'ACTIVE'
    --and v$session.sid = 97
    --and v$session.username = 'SYSTEM'
    --and v$process.spid = 24301
    ORDER BY pga_used_mem DESC"""

mem2 = """select sn.INSTANCE_NUMBER, sga.allo sga, pga.allo pga,(sga.allo+pga.allo) tot,trunc(SN.END_INTERVAL_TIME,'mi') time
     from
   (select snap_id,INSTANCE_NUMBER,round(sum(bytes)/1024/1024/1024,3) allo
      from DBA_HIST_SGASTAT
     group by snap_id,INSTANCE_NUMBER) sga
   ,(select snap_id,INSTANCE_NUMBER,round(sum(value)/1024/1024/1024,3) allo
       from DBA_HIST_PGASTAT where name = 'total PGA allocated'
      group by snap_id,INSTANCE_NUMBER) pga
   , dba_hist_snapshot sn
   where sn.snap_id=sga.snap_id
     and sn.INSTANCE_NUMBER=sga.INSTANCE_NUMBER
     and sn.snap_id=pga.snap_id
     and sn.INSTANCE_NUMBER=pga.INSTANCE_NUMBER
   order by sn.snap_id desc, sn.INSTANCE_NUMBER
   """


listener_log = "select logtime1,connect1, protocol1,action1,service1 from listenerlog"


active_instance = "SELECT * FROM V$ACTIVE_INSTANCES"


schemastatgather = """
BEGIN
      DBMS_STATS.gather_schema_stats (
      ownname => 'rimon',
      ESTIMATE_PERCENT  => dbms_stats.auto_sample_size,
      degree   => 4);
END;
"""

tablestatgather = """
 exec dbms_stats.gather_table_stats(ownname=>'',tabname=>'',estimate_percent=>DBMS_STATS.AUTO_SAMPLE_SIZE,cascade=>TRUE,degree =>4)
"""

indexstatgather = """
  exec DBMS_STATS.GATHER_INDEX_STATS(ownname => '&OWNER',indname =>'&INDEX_NAME',estimate_percent =>DBMS_STATS.AUTO_SAMPLE_SIZE)
"""

systemstatgather = """
 execute dbms_stats.gather_system_stats('interval',60)
"""
#exec dbms_stats.gather_schema_stats(ownname=>'shadman',ESTIMATE_PERCENT=>dbms_stats.auto_sample_size,degree =>4);


statgather = {
    'schemastatgather' : schemastatgather,
    'tablestatgather': tablestatgather,
    'indexstatgather': indexstatgather,
    'systemstatgather' : systemstatgather
}







