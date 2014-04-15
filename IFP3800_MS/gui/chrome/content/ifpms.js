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

    this.config_sid = 0;        //最新流水号
    this.alarm_sid = 0;         //最新流水号
    this.config_saved_sid=0;      //已保存的流水号
    this.alarm_saved_sid=0;       //已保存的流水号

    this.dc_key = ["did","product_type","ipaddr","name","cx","cy","medium_type","sensitivity","sensitivity2","env_factor",
        "sid","mac","desc","status", "pa_num","latest_change_time","hw_version","sw_version","protocol_ver"];
    this.pa_key = ["did","pid","name","desc","enable","cx","cy","work_mode","process_mode",
                   "alarm_resp_time","alarm_sensitivity","alarm_resistant_factor","alarm_resistant_factor_gsd","sensitivity",
                   "enable","enable_start","enable_end",'sample_path',
                   'sample_pid','sample_startstamp','sample_endstamp','sample_currentstamp','sample_import_rate','fft_begin','fft_end','fft_noise_value','fft_magic_value',
                   "sid"];

    this.cus_filename = GREUtils.File.chromeToPath("chrome://etc/content/custom.conf");
    this.def_filename = GREUtils.File.chromeToPath("chrome://etc/content/default.conf");
 
    // 读全局配置
 
    if(GREUtils.File.exists(this.cus_filename)) //用户配置文件存在
    {   
        try
        {
            GREUtils.log("Ifpms.Config() load config from custom.conf");
            this.conf = GREUtils.JSON.decodeFromFile(this.cus_filename);
        }
        catch(err)
        {
            GREUtils.log("Ifpms.Config() load config from default.conf");
            this.conf = GREUtils.JSON.decodeFromFile(this.def_filename);
        }
    } else {
        GREUtils.log("Ifpms.Config() load config from default.conf");
        this.conf = GREUtils.JSON.decodeFromFile(this.def_filename);
    }

    //保留原始设置
    if(this.conf.hasOwnProperty("mapUrl")){
        this.mapUrl = this.conf['mapUrl'];
    } else {
        this.mapUrl = "chrome://ifpms/skin/images/map/default.png";
    }
    GREUtils.log("map Url is :" + this.mapUrl);

    if(this.conf.hasOwnProperty("paIcon")){
        this.paIcon = this.conf['paIcon'];
    } else {
        this.paIcon = "18";
    }


    var thiz = this;


    this.fresh = function() {
        thiz.increase_config();
    };

    this.increase_config = function(){
        thiz.config_sid = thiz.config_sid + 1;        //最新流水号递增
    };

    this.increase_alarm = function(){
        thiz.alarm_sid = thiz.alarm_sid + 1;          //最新流水号递增
    };

    this.save = function() {
        
        //保存新增告警
        if ( thiz.alarm_saved_sid != thiz.alarm_sid ) {
            thiz.alarm_saved_sid = thiz.alarm_sid;
            GREUtils.log("Ifpms.Config.save() export alarm history.");
            Global_SaveAlarmlist(); //保存告警记录
            //save
        }

        //保存变更配置
        if ( thiz.config_saved_sid != thiz.config_sid ) {

            var new_conf={};
            new_conf.dc = [];
            thiz.config_saved_sid = thiz.config_sid;
            GREUtils.log("Ifpms.Config.save() export config.");

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
                new_conf.dc.push(dc_conf);
            }       
            
            new_conf.userinfo=get_alluserinfo();//保存用户账号信息
            new_conf.mapUrl= thiz.mapUrl; //getMapImgURL();//地图背景图片
            new_conf.paIcon=thiz.paIcon;//防区图标大中小
            new_conf.waveChecked=wavechecked;
            new_conf.alarmSoundtime=alarmSoundtime;
            new_conf.alarmMax=global_alarmlistlength;//最大告警长度
            new_conf.wavestart=document.getElementById('sampleNumber').value;//波形起点
            new_conf.waveend=document.getElementById('sample_end').value;//波形终点
            new_conf.wavelayout=document.getElementById('layoutType').value;
            new_conf.alarmprocmode=global_alarmproc_mode;

            var canids=['wave_canvas','sec_wave','third_wave','fourth_wave'];//波形参数设置信息
            new_conf.wavesetting=[];
            for(var i in canids)
            {
              new_conf.wavesetting.push(document.getElementById(canids[i]).saveConfig());
            }
            GREUtils.JSON.encodeToFile(thiz.cus_filename,new_conf);  
        }

    };
};

