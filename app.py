from flask import Flask
from config import app_config
from flask_restful import Api
import psutil
from queryclass import Systeminfo, Basicinfo, Temptablespace, Tbsdetail, Defaulttbs, Userspaceused, Tbsquota, Frastatus, \
    Recousage, Datafileusage, Loginfo, Alertlog, Rmanstartnstop, Rmanrunning, Rmanhistory, Listenerlog, Lockedobj, \
    Pgainfo, Asmdiskinfo, Asmstatinfo,Racinstance,Sshconnectivity,Statgather


def create_app(env_name):
    """
    Create app
    """

    # app initiliazation
    app = Flask(__name__)

    app.config.from_object(app_config[env_name])
    api = Api(app)

    api.add_resource(Systeminfo, '/sysinfo')
    api.add_resource(Basicinfo, '/basicinfo')
    api.add_resource(Temptablespace, '/temptbslist')
    api.add_resource(Tbsdetail, '/tbslist')
    api.add_resource(Defaulttbs, '/defaulttbslist')
    api.add_resource(Userspaceused, '/userspaceused')
    api.add_resource(Tbsquota, '/tbsquota')
    api.add_resource(Frastatus, '/fralist')
    api.add_resource(Recousage, '/recolist')

    api.add_resource(Datafileusage, '/datafilelist')
    api.add_resource(Loginfo, '/loginfo')
    api.add_resource(Alertlog, '/alertlog')
    api.add_resource(Rmanstartnstop, '/rmanstartnstop')
    api.add_resource(Rmanrunning, '/rmanrunning')
    api.add_resource(Rmanhistory, '/rmanhist')
    api.add_resource(Listenerlog, '/listenerlog')
    api.add_resource(Lockedobj, '/lockedobj')
    api.add_resource(Pgainfo, '/pgainfo')
    api.add_resource(Asmdiskinfo, '/asmdiskinfo')
    api.add_resource(Asmstatinfo, '/asmstatinfo')
    api.add_resource(Racinstance, '/racstat')
    api.add_resource(Sshconnectivity, '/ssh')
    api.add_resource(Statgather, '/statgather')





   # api.add_resource(TableIndexStat, '/tableindexstat')


    return app

