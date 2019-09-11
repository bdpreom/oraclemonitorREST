#LISTENER LOG COLLECT

create directory LISTENERDIR as '';


create table listenerlog
(
   logtime1 timestamp,
   connect1 varchar2(300),
   protocol1 varchar2(300),
   action1 varchar2(15),
   service1 varchar2(15),
   return1 number(10)
)
organization external (
   type oracle_loader
   default directory LISTENERDIR
   access parameters
   (
      records delimited by newline
      nobadfile
      nologfile
      nodiscardfile
      fields terminated by "*" lrtrim
      missing field values are null
      (
          logtime1 char(30) date_format
          date mask "DD-MON-YYYY HH24:MI:SS",
          connect1,
          protocol1,
          action1,
          service1,
          return1
      )
   )
   location ('listener.log')
)
reject limit unlimited;


#ALERTLOG COLLECT


SQL> conn / as sysdba
SQL> create view v_$alert_log as select * from x$dbgalertext;
SQL> create public synonym v$alert_log for sys.v_$alert_log;
SQL> grant select on v$alert_log to MON_USER;
SQL> conn user/passwd

SQL> select count(*) from v$alert_log;
COUNT(*)
———-
43171
SQL>
Now we have the possibility to select the values from the X$DBGALERTEXT table in SYS schema.
With the following select statement you get all ORA- errors during the last hour:
SQL> show user;
USER is “sys”
SQL> SELECT
     to_char(originating_timestamp,’DD.MM.YYYY HH24:MI:SS’),
     message_text
     FROM
     v$alert_log
    WHERE originating_timestamp > systimestamp – 1/24
    and REGEXP_LIKE (message_text, ‘(ORA-)’);