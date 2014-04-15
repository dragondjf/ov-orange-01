var Cc = Components.classes;
var Ci = Components.interfaces;



Ifpms.Xpcom = new function() {

    this.DCMgmt = Cc["@ov-orange.com/pyIfpmsDCMgmt;1"].
				getService(Ci.nsIPyIfpmsDCMgmt);

    this.servEvent = {
        onRaise: function (did, pid, alm_type, alm_id, alm_time) {
		        //jsdump("device:" + did+'-'+pid + ", status: "+ alm_type + ", alm_id:" + alm_id );
            if (Ifpms.Xpcom.DCMgmt.dc_list.length>=2 && Ifpms.Xpcom.DCMgmt.getDC(2)!=null){
            var pa=Ifpms.Xpcom.DCMgmt.getDC(2).getPA(2);
            if(did == 2 && pid == 2 && pa.work_mode == 2 && alm_type == 4){
              alm_type = 9;
            }
            else if(did == 2 && pid == 2 && pa.work_mode == 2 && alm_type == 2){
              alm_type = 10;
            }
          }
            Ifpms.PaMgr.changeStatus (did,pid,alm_type);
            Ifpms.Map.changeStatus (did,pid,alm_type);

            while (Ifpms.Xpcom.DCMgmt.alarm_history.length > global_alarmlistlength ) {
              Ifpms.Xpcom.DCMgmt.alarm_history.removeElementAt(0);
              GREUtils.log("clear alarm ...");
            }

            Ifpms.Config.increase_alarm();
            
            if (alm_id != 0) {
                alarmobservernotify(did,pid,alm_type,alm_time,alm_id);//by  LY 2011-11-10 
            }
            if (alm_type == NODE_STATUS_ALARM_CRITICAL
               || alm_type == NODE_STATUS_ALARM_BLAST
               || alm_type == NODE_STATUS_ALARM_FIBER_BREAK) {
               GREUtils.Sound.play("chrome://ifpms/content/media/warn.wav");
            } else if (alm_type == NODE_STATUS_DISCONN ) {
               GREUtils.Sound.play("chrome://ifpms/content/media/notify.wav");
            } else {
            }
        }
    };

    this.startup = function () {
   		this.DCMgmt.start(this.servEvent);

    };
    
	this.shutdown = function () {
   		this.DCMgmt.stop();
    }
    
};
