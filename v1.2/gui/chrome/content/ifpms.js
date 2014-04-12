// application.js

/* 节点状态 */
const NODE_STATUS_DISABLE      = 0;
const NODE_STATUS_DISCONN      = 1;
const NODE_STATUS_CONNECT      = 2;
const NODE_STATUS_ALARM_MINOR      = 3;
const NODE_STATUS_ALARM_CRITICAL   = 4;
const NODE_STATUS_ALARM_FIBER_BREAK = 5;
const NODE_STATUS_ALARM_BLAST = 6;

/* 节点状态css样式类名称 */
const node_status_css_class = ["disable","disconn","connect","alarm_minor","alarm_critical", "alarm_fiber_break", "alarm_blast","Lid-open","Lid-close","rain_wind","start"];

function jsdump(str)
{
  Components.classes['@mozilla.org/consoleservice;1']
            .getService(Components.interfaces.nsIConsoleService)
            .logStringMessage(str);
}

var Ifpms = {
    version: '0.5.1',
    timer:0,
    shutdown: function() {
      //  this.Config.save();
      //取消自动保存配置 by ly 2011-9-29
       //结束程序时关闭可能打开的帮助窗口 by 2011-12-29
	   if(typeof(global_hlpwindow1.name)!='undefined')
	   {
	      global_hlpwindow1.close();
	   }
	   //jsdump(typeof(global_alarmproc_win));
	   if(typeof(global_alarmproc_win)!='undefined')
	   {
	     global_alarmproc_win.close();
	   }
	   for(var  i in global_alarmwins)
	   {
	    // jsdump("wintype"+typeof(global_alarmwins[i]));
	    if(typeof(global_alarmwins[i])!='undefined')
		{
		  global_alarmwins[i].close();
		}
	   }
	},
    // Initialization
    initialize: function() {
        // full screen
        window.setTimeout('window.fullScreen = true;', 1);
        // show datetime   
        document.getElementById('lblDatetime').value = new Date().toLocaleString();
        window.setInterval("document.getElementById('lblDatetime').value = new Date().toLocaleString();", 1000);
        Ifpms.timer=0;
    },
    clearSound:function(){
	window.opener.clearInterval(window.opener.Ifpms.timer);
	window.opener.Ifpms.timer=0;
    }
};
  
Ifpms.Config = new function() {
  //  this.uri = "chrome://ifpms/content/etc/config.js";
    this.uri=global_configuri;//by ly 2011-9-29 
    this.dc_key = ["did","product_type","ipaddr","mac","name","cx","cy","medium_type","sensitivity","sensitivity2","env_factor","protocol_ver"];
    this.pa_key = ["did","pid","name","desc","enable","cx","cy","work_mode","process_mode",
                   "alarm_resp_time","alarm_sensitivity","alarm_resistant_factor","alarm_resistant_factor_gsd","sensitivity",
                   "enable","enable_start","enable_end",'sample_path',
                   'sample_pid','sample_startstamp','sample_endstamp','sample_currentstamp','sample_import_rate','fft_begin','fft_end','fft_noise_value','fft_magic_value'];
    this.file = GREUtils.File.chromeToPath(this.uri);
    this.saved = false;
    var thiz = this;
    
    try
    {
        this.conf = GREUtils.JSON.decodeFromFile(this.file);
    }
    catch(err)
    {
       this.conf = {};
    }


    this.fresh = function() {
        thiz.saved = false;
    };

    this.save = function() {

        thiz.conf.dc = [];
        
        for (var i=0; i< Ifpms.Xpcom.DCMgmt.dc_list.length; i++) {
            var dc_conf = {}
            var dc = Ifpms.Xpcom.DCMgmt.dc_list.queryElementAt(i,Components.interfaces.nsIPyIfpmsDC);
            if (dc) {
                for (var n in thiz.dc_key) {
                    dc_conf[thiz.dc_key[n]] = dc[thiz.dc_key[n]];
                }

                dc_conf["pa"] = [];

                for (var j=0;j<dc.pa_list.length;j++) {
                    var pa_conf = {}
                    var pa = dc.pa_list.queryElementAt(j,Components.interfaces.nsIPyIfpmsPA);
                    if (pa) {
                        for (var m in thiz.pa_key) {
                            pa_conf[thiz.pa_key[m]] = pa[thiz.pa_key[m]];
                        }
                    }
                    dc_conf["pa"].push(pa_conf);
                }
            }
            thiz.conf.dc.push(dc_conf);
        }
        
        GREUtils.JSON.encodeToFile(thiz.file,thiz.conf);
         thiz.saved = false;       
    };
};

