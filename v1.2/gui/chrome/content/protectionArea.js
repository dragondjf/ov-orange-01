
Ifpms.PaMgr = {
  load: function pa_load() {
    var dc_conf = Ifpms.Config.conf.dc;
    this.paList = document.getElementById("palist");
    this.lastSelectedItem = null;
    for ( i in dc_conf ) {
        var o = dc_conf[i];
        var retcode={}, did = o.did, dc=null;
        if(o.pa_num == 4){
          document.getElementById("Q_workmodes").style.display="block";
        }

        dc = Ifpms.Xpcom.DCMgmt.createDC(o.product_type,o.ipaddr,o.pa_num,did,retcode);
        
        if (dc && retcode.value == 0) {

          for (var n in Ifpms.Config.dc_key) {
              if (o[Ifpms.Config.dc_key[n]]) {
                dc[Ifpms.Config.dc_key[n]] = o[Ifpms.Config.dc_key[n]];
              }
          }

          jsdump("dc.pa_list.length is " + dc.pa_list.length);

          for (var j=0; j< dc.pa_list.length; j++) {

              var pa = dc.pa_list.queryElementAt(j,Components.interfaces.nsIPyIfpmsPA);
              jsdump("pa.did is "+pa.did)

              if (o["pa"] && o["pa"][j]) {
                var p = o["pa"][j];
                for (var m in Ifpms.Config.pa_key) {
                  if (p[Ifpms.Config.pa_key[m]] !== undefined ) {
                    pa[Ifpms.Config.pa_key[m]] = p[Ifpms.Config.pa_key[m]];
                    jsdump("set PA["+Ifpms.Config.pa_key[m]+"] with "+p[Ifpms.Config.pa_key[m]]);
                  }
                }
              } else {
                pa.cx = 40*pa.pid
                pa.cy = 40*pa.did
              }
              
              Ifpms.Map.nodes[pa.sid] = new Ifpms.Map.MapNode(pa);
              var elt = document.createElement("richlistitem");
              elt.setAttribute("permission",global_currentusertype);
              this.paList.appendChild(elt);
              elt.build(pa);
          }


        } else {
          jsdump("retcode is "+ retcode.value)
        }
    }
    window.addEventListener("unload", this.unload, false);
    this._alarmInterval = setInterval(this.flashlight, 1000);
  },
  unload: function pa_unload() {
    clearInterval(this._alarmInterval);
  },
  flashlight: function pa_flashlight() {
  },
  _updateList: function pa__updateList() {
  },
  observe: function pa_observe(aObject, aTopic, aData) {
  },
  pa_delete: function pa_delete() {
    // show prompt


    if (!this.paList.selectedItem)
      return false;
       
    var did = this.paList.selectedItem.xobj.did;
    var bundle = document.getElementById("paBundle");

    if ( GREUtils.Dialog.confirm(bundle.getString("delComfirm"),bundle.getString("delContent")) ){

      Ifpms.Xpcom.DCMgmt.removeDC(did);

      // remove from ui
      $('[did="'+did+'"]').remove();
      
      this.paList.selectedIndex = null;
      this.paList.selectedItem = null;
      this.lastSelectedItem = null;

    }

  },
  pa_new: function pa_new() {
    this.openDialog("chrome://ifpms/content/protectionAreaNew.xul");
  },
  Q_workmodeChange:function Q_workmodeChange(){
    this.openDialog("chrome://ifpms/content/changeWorkMode_Q.xul");
  },
  edit: function pa_edit() {
    //alert(this.paList.selectedItem.xobj.dc.product_type);
    if(this.paList.selectedItem.xobj.dc.product_type!=0&&this.paList.selectedItem.xobj.pid==2){
      return;
    }
    this.openDialog("chrome://ifpms/content/protectionAreaEdit.xul",this.paList.selectedItem);
    
  },
  enable_audio_monitor: function enable_audio_monitor(enable) {
    
    if (this.paList.selectedItem) {
      this.paList.selectedItem.xobj.audio_enable = enable;
      this.paList.selectedItem.xobj.dc.audio_enable = enable;
      this.paList.selectedItem.xobj.dc.sync(10, this.paList.selectedItem.xobj.pid); //SET_SWITCH_CTRL_REQ
    }
  },
  close: function pa_close() {
    // If a modal dialog is opened, we can't close this window now
    if (this.modalDialog)
      setTimeout(function() { window.close();}, 0);
    else
      window.close();
  },
  select: function pa_select(sid) {
    this.paList.selectedItem = document.getElementById("item-"+sid);
    var idx = this.paList.getIndexOfItem(this.paList.selectedItem);
    this.paList.scrollToIndex(idx);
  },
  onItemSelect: function pa_onItemSelect() {

    this.lastSelectedItem = this.paList.selectedItem;

    $('#map > [selected="true"]').attr("selected",false);
    $("#cricle-"+this.paList.selectedItem.xobj.sid).attr("selected",true);
/* by ly 2011-9-27 --*/
//判断权限 
    if(global_currentusertype<1)//值班员
    {
        this.paList.selectedItem.PermissionCheck();
    }
/*######*/
  },
  openDialog: function pa_openDialog(aUrl, aArgs) {
    this.modalDialog = true;
    window.openDialog(aUrl, "", "chrome,modal,titlebar,centerscreen,resizable=yes", aArgs);
    this.modalDialog = false;
  },
  changeStatus : function(did, pid, status) {
    var itemid = '';
    if (pid != 0 && status != 7 && status != 8) {
      itemid = 'item-PA-'+did+'-'+pid;
      jsdump(itemid+" status is "+ node_status_css_class[status]);
      var elem = document.getElementById(itemid);
      jsdump(itemid+" xobj status is "+ node_status_css_class[elem.xobj.status] + "("+elem.xobj.status+")");
      if (elem) {
        elem.setAttribute("class",node_status_css_class[status]);
        elem.refresh();
      }      
    } 
  }
};

Ifpms.Pa = {
  onload: function pa_onload() {
    this.elm = window.arguments[0];
    this.xobj = this.elm.xobj;
    
    var pa=Ifpms.Xpcom.DCMgmt.getDC(this.xobj.did).getPA(this.xobj.pid);
    //jsdump(pa.sample_startstamp);
    document.getElementById("pBegin").value=pa.fft_begin;
    document.getElementById("pEnd").value=pa.fft_end;
    document.getElementById("noise_value").value=pa.fft_noise_value;
    document.getElementById("magic_value").value=pa.fft_magic_value;
    document.getElementById("fft_size").value=pa.fft_size;
    document.getElementById("fft_style").vlaue=pa.fft_style;
    
    document.getElementById("edit_ipaddr").value=this.xobj.dc.ipaddr;
    document.getElementById("pa_editChannelNum").value=pa.sample_pid;
    document.getElementById("sample_editPath").value=pa.sample_path;
    document.getElementById("editStartDate").value=new Date(pa.sample_startstamp*1000).format("yyyy-MM-dd");
    document.getElementById("editStartTime").value=new Date(pa.sample_startstamp*1000).format("hh:mm:ss");
    document.getElementById("editEndDate").value=new Date(pa.sample_endstamp*1000).format("yyyy-MM-dd");
    document.getElementById("editEndTime").value=new Date(pa.sample_endstamp*1000).format("hh:mm:ss");
    document.getElementById("log_num").value=pa.sample_import_rate;
    
    document.getElementById("sid").value = this.xobj.sid;
    document.getElementById("name").value = this.xobj.name;
    document.getElementById("desc").value = this.xobj.desc;
    document.getElementById("enable").checked = this.xobj.enable;
    document.getElementById("enable_start").value=this.xobj.enable_start;
    document.getElementById("enable_end").value=this.xobj.enable_end;
    document.getElementById("crood").value = ""+this.xobj.cx+":"+this.xobj.cy;
    document.getElementById("work_mode").value = this.xobj.work_mode;
    document.getElementById("process_mode").value = this.xobj.process_mode;
    document.getElementById("alarm_resp_time").value = this.xobj.alarm_resp_time;
    
    document.getElementById("alarm_resistant_factor").value = this.xobj.alarm_resistant_factor;
    document.getElementById("alarm_resistant_factor_gsd").value = this.xobj.alarm_resistant_factor_gsd;
    document.getElementById("sensitivity").value = this.xobj.sensitivity;
                   
    document.getElementById("medium_type").value = this.xobj.dc.medium_type;
    document.getElementById("sensitivity2").value = this.xobj.dc.sensitivity2;
    document.getElementById("env_factor").value = this.xobj.dc.env_factor;

    document.getElementById("ipaddr").value = this.xobj.dc.ipaddr;
    document.getElementById("mac").value = this.xobj.dc.mac;
    document.getElementById("product_id").value = this.xobj.dc.product_id;
    document.getElementById("hw_version").value = this.xobj.dc.hw_version;
    document.getElementById("sw_version").value = this.xobj.dc.sw_version;
    document.getElementById("machine_id").value = this.xobj.dc.machine_id;
    document.getElementById("slot_id").value = this.xobj.dc.slot_id;
    document.getElementById("protocol_ver").value = this.xobj.dc.protocol_ver;

    this.changeworkvalue(this.xobj.work_mode);
    document.getElementById("alarm_sensitivity").value = this.xobj.alarm_sensitivity;

    var MU_factor=document.getElementById("sensitivity");
    if(document.getElementById("protocol_ver").value==1)
    {
      document.getElementById("process_mode1").setAttribute("style","display:none");
      document.getElementById("process_mode3").setAttribute("style","display:none");
      document.getElementById("process_mode").value = 2;
    }
    else
    {
      document.getElementById("process_mode1").setAttribute("style","display:block");
      document.getElementById("process_mode3").setAttribute("style","display:block");
    }
    if(document.getElementById("work_mode2")!=null){
      if(this.xobj.pid == 4 && getCurrentSysPath() == "default"){
        document.getElementById("work_mode2").setAttribute("style","display:block");
      }
      else
      {
        document.getElementById("work_mode2").setAttribute("style","display:none");
      }
    }

    //非日志类型 采集器 隐藏样本参数设置 
   if(this.xobj.dc.product_type!=2&&this.xobj.dc.product_type!=4)
   {
     document.getElementById("algorithm_para").style.display="none";
     document.getElementById("sample_argu").style.display="none";
   }
   else{
     document.getElementById("algorithm_para").style.display="none";
   }
  },
  
  unload: function pa_unload() {
  },
  ChangeSamplePath:function(getid){// choose new sample path 
    var nsIFilePicker = Components.interfaces.nsIFilePicker;
    var fp = Components.classes["@mozilla.org/filepicker;1"].createInstance(nsIFilePicker);
    //var strbun=document.getElementById('debugstr');
    fp.init(window, "", nsIFilePicker.modeGetFolder);
    var res=fp.show();
   if(nsIFilePicker.returnOK==res)
    {
       //filepath=GREUtils.File.append(fp.file.path,filename);
       //return fp.file.path;
	document.getElementById(getid).value=fp.file.path;
    }
    else{
	
	
	}
  
  
  },

  getProcessModeValue: function(the){
       if(the.value==1){ 
        document.getElementById("process_mode").value=2;
        document.getElementById("process_mode1").setAttribute("style","display:none");
        document.getElementById("process_mode3").setAttribute("style","display:none");
        document.getElementById("sensitivity").setAttribute("max","255");
        document.getElementById("sensitivity").setAttribute("min","0");
    }
       if(the.value==2){ 
          if(getCurrentSysPath()=="default")
          {
            document.getElementById("process_mode").value=1;
            // document.getElementById("process_mode1").setAttribute("style","display:block");
          }
          else
          {
            document.getElementById("process_mode").value=3;
            // document.getElementById("process_mode1").setAttribute("style","display:none");
          }
          document.getElementById("process_mode1").setAttribute("style","display:block");
          document.getElementById("process_mode3").setAttribute("style","display:block");
          document.getElementById("sensitivity").setAttribute("max","65000");
          document.getElementById("sensitivity").setAttribute("min","2");
      }
  },
  changeworkvalue: function changeworkvalue(workmode){
    // if (workmode==6){
    //   document.getElementById("alarm_sensitivity").setAttribute("max","65536");
    //   document.getElementById("alarm_sensitivity").setAttribute("min","1");
    // }
    // else{
    //   document.getElementById("alarm_sensitivity").setAttribute("max","300");
    // }
  },

  getWorkModeValue:function get_value(the){
    var workValue=the.value;
    this.changeworkvalue(workValue);
    //var sensitivity=document.getElementById("alarm_sensitivity");
    //var alarm_resp_time=document.getElementById("alarm_resp_time");
    //var alarm_resistant_factor=document.getElementById("alarm_resistant_factor");
    //if(workValue==4)
    //{
    //  sensitivity.setAttribute("max","2000")
    //  sensitivity.setAttribute("value","80");
    //  alarm_resp_time.setAttribute("value","2");
    //  alarm_resistant_factor.setAttribute("value","5");
    //}
    //else{
    //  sensitivity.setAttribute("max","16384");
    //  sensitivity.setAttribute("value","1024");
    //  alarm_resp_time.setAttribute("value","2");
    //  alarm_resistant_factor.setAttribute("value","5");
    //}
  },
  Q_save: function Q_save(){
    var workmode_type = document.getElementById("Q_workmode_type").value;
    var dc_num = document.getElementById("dc_num").value;
    var dc=window.opener.Ifpms.Xpcom.DCMgmt.getDC(dc_num);
    if (dc_num > window.opener.Ifpms.Xpcom.DCMgmt.dc_list.length){
      alert('输入采集器的编号必须小于等于'+ window.opener.Ifpms.Xpcom.DCMgmt.dc_list.length);
    }
    if (workmode_type == 9){
      dc.protocol_ver = 3;
      dc.Q_workmode = 1;
    }
    else if(workmode_type == 10){
      dc.protocol_ver =3;
      dc.Q_workmode = 0;
    }
    dc.sync(3,workmode_type);
  },
  save: function pa_save() {

    var sync_flag = false;
    var fBegin=document.getElementById("pBegin").value;
    var fEnd=document.getElementById("pEnd").value;
    var f_noise_value=document.getElementById("noise_value").value;
    var f_magic_value=document.getElementById("magic_value").value;
    var fft_size=document.getElementById("fft_size").value;
    var fft_style=document.getElementById("fft_style").value;
    //var edit_ip=document.getElementById("edit_ipaddr").value;
    var editNum=document.getElementById("pa_editChannelNum").value;
    var editPath=document.getElementById("sample_editPath").value;

    var editStartDate=document.getElementById("editStartDate").value;
    var editStartTime=document.getElementById("editStartTime").value;
    var editThisTime=editStartDate+"-"+editStartTime;
    var new_editThisTime=editThisTime.replace(/:/g,'-');
    var editStartArr=new_editThisTime.split('-');
    var eidtStartTimestamp=parseInt(new Date(editStartArr[0],editStartArr[1]-1,editStartArr[2],editStartArr[3],editStartArr[4],editStartArr[5]).getTime())/1000;  
    var editEndDate=document.getElementById("editEndDate").value;
    var editEndTime=document.getElementById("editEndTime").value;
    var editThisEndTime=editEndDate+"-"+editEndTime;
    var new_editThisEndTime=editThisEndTime.replace(/:/g,'-');
    var editEndArr=new_editThisEndTime.split('-');
    var editEndTimestamp=parseInt(new Date(editEndArr[0],editEndArr[1]-1,editEndArr[2],editEndArr[3],editEndArr[4],editEndArr[5]).getTime())/1000;
    var logNum=document.getElementById("log_num").value;
    
    this.xobj.name = document.getElementById("name").value;
    this.xobj.desc = document.getElementById("desc").value;
    this.xobj.enable = document.getElementById("enable").checked;
    this.xobj.enable_start=document.getElementById("enable_start").value;
    this.xobj.enable_end=document.getElementById("enable_end").value;
    this.xobj.work_mode=document.getElementById("work_mode").value;
    this.xobj.process_mode=document.getElementById("process_mode").value;
    this.xobj.dc.protocol_ver=document.getElementById("protocol_ver").value;
    this.xobj.sensitivity = document.getElementById("sensitivity").value;

          

    this.xobj.alarm_resp_time = document.getElementById("alarm_resp_time").value;
    this.xobj.alarm_sensitivity = document.getElementById("alarm_sensitivity").value;
    this.xobj.alarm_resistant_factor = document.getElementById("alarm_resistant_factor").value;
    this.xobj.alarm_resistant_factor_gsd = document.getElementById("alarm_resistant_factor_gsd").value;
    this.xobj.dc.sync(7, this.xobj.pid);  //SET_CHANNEL_CTRL_REQ

    var reimport=false;
    var newip=document.getElementById("edit_ipaddr").value;
    var bundle = document.getElementById("paBundle");
    if(newip==""){
      document.getElementById("saveError").value=bundle.getString("invalidIP");
      return false;
    }else if(eidtStartTimestamp<0){
      document.getElementById("saveError").value=bundle.getString("startTimeError");
      return false;
    }else if(editEndTimestamp<0){
      document.getElementById("saveError").value=bundle.getString("endTimeError");
      return false;      
    }else if(eidtStartTimestamp>editEndTimestamp){
      document.getElementById("saveError").value=bundle.getString("timeError");
      return false;      
    }else if(this.xobj.work_mode==0){
      document.getElementById("saveError").value=bundle.getString("select_wordMode");;
      return false;
    }
    if(this.xobj.dc.ipaddr!=newip)
    {
       this.xobj.dc.ipaddr=newip;
       reimport=true;
    }
    
    // if(this.xobj.did ==2 && this.xobj.pid == 2 &&this.xobj.work_mode == 2)
    // {
    //   this.xobj.name = "环境自适应探测器";
    //   for (var i=0; i< 2 ; i++){
    //     var dc = Ifpms.Xpcom.DCMgmt.getDC(i+1);
    //     for (var j=0; j< dc.pa_list.length; j++) {
    //         var pa = dc.pa_list.queryElementAt(j,Components.interfaces.nsIPyIfpmsPA);
    //         if(pa.work_mode != 2){
    //           pa.name = "防区" + pa.did +"-"+ pa.pid + "(灵敏度自适应)";
    //           var itemsid = 'item-PA-'+pa.did+'-'+pa.pid;
    //           var elems = window.opener.document.getElementById(itemsid);
    //           if (elems) {
    //             elems.refresh();
    //           }
    //         }
    //       }
    //   }
    // }
    // else if(this.xobj.did ==2 && this.xobj.pid == 2 &&this.xobj.work_mode == 1)
    // {
    //   //this.xobj.name = "防区" + this.xobj.did +"-"+ this.xobj.pid;
    //   this.xobj.name = document.getElementById("name").value;
    //   for (var i = 0; i< 2 ; i++) {
    //     var dc = Ifpms.Xpcom.DCMgmt.getDC(i+1);
    //     for (var j=0; j< dc.pa_list.length; j++) {
    //         var pa = dc.pa_list.queryElementAt(j,Components.interfaces.nsIPyIfpmsPA);
    //         if(pa.work_mode != 2){
    //           if(i ==1 && j == 1){
    //             pa.name = document.getElementById("name").value;
    //           }else{
    //             pa.name = "防区" + pa.did +"-"+ pa.pid;
    //           }
    //           var itemsid = 'item-PA-'+pa.did+'-'+pa.pid;
    //           var elems = window.opener.document.getElementById(itemsid);
    //           if (elems) {
    //             elems.refresh();
    //           }
    //         }
    //       }
    //   }
    // }

    var pa=Ifpms.Xpcom.DCMgmt.getDC(this.xobj.did).getPA(this.xobj.pid);

    pa.fft_begin=fBegin;
    pa.fft_end=fEnd;
    pa.fft_noise_value=f_noise_value;
    pa.fft_magic_value=f_magic_value;
    pa.fft_size=fft_size;
    pa.fft_style=fft_style;
    
   if(pa.sample_pid!=editNum)
   {
       pa.sample_pid=editNum;
       reimport=true;
   }   
   if(pa.sample_path!=editPath)
   {
       pa.sample_path=editPath;
       reimport=true;
   }
    if(pa.sample_startstamp!=parseInt(eidtStartTimestamp))
	{
	    pa.sample_startstamp=eidtStartTimestamp;
	     reimport=true;
	}
    if(pa.sample_endstamp!=parseInt(editEndTimestamp))
    {
        pa.sample_endstamp=editEndTimestamp;
        reimport=true;
     }
	 jsdump(reimport);
	 if(reimport)
	 {
	 this.xobj.dc.sample_config_changed=true;//需要重新 启动导入 日志
	 }
    
    //alert(this.xobj.dc.sample_config_changed);
    pa.sample_import_rate=logNum;
    jsdump("sample rate : "+pa.sample_import_rate);

    this.elm.refresh();
    Ifpms.Map.PAnotify(this.xobj.sid);// refresh nodes on the map 
  
  },
  pa_new: function pa_new() {
    var pa_num = 2;
    var dc_type = document.getElementById("dc_type").value;
    if (dc_type == 6){
      pa_num = 4;
      window.opener.document.getElementById("Q_workmodes").style.display="block";
    }
    else if (dc_type === 0) {
      pa_num = 2;
    }
    else if (dc_type == 5) {
      return this.domain_new();
    }
    var ipaddr = document.getElementById("ipaddr"+dc_type).value;
    var paChannelNum = document.getElementById("paChannelNum").value;
    var logPath=document.getElementById("sample_path").value;
    
    var startDate=document.getElementById("startDate").value;
    var startTime=document.getElementById("startTimes").value;
    var thisTime=startDate+"-"+startTime;
    var new_thisTime=thisTime.replace(/:/g,'-');
    var startArr=new_thisTime.split('-');
    var startTimestamp=parseInt(new Date(startArr[0],startArr[1]-1,startArr[2],startArr[3],startArr[4],startArr[5]).getTime())/1000;  
    var endDate=document.getElementById("endDate").value;
    var endTime=document.getElementById("endTimes").value;
    var thisEndTime=endDate+"-"+endTime;
    var new_thisEndTime=thisEndTime.replace(/:/g,'-');
    var endArr=new_thisEndTime.split('-');
    var endTimestamp=parseInt(new Date(endArr[0],endArr[1]-1,endArr[2],endArr[3],endArr[4],endArr[5]).getTime())/1000;
    var bundle = document.getElementById("paBundle"); 
    var ipRegex = /^(\d{1,2}|1\d{2}|2[0-4]\d{1}|25[0-5])\.(\d{1,2}|1\d{2}|2[0-4]\d{1}|25[0-5])\.(\d{1,2}|1\d{2}|2[0-4]\d{1}|25[0-5])\.(\d{1,2}|1\d{2}|2[0-4]\d{1}|25[0-5])$/;

    if(ipaddr=="" || !ipRegex.test(ipaddr)){
      document.getElementById("error").value =bundle.getString("invalidIP");
      return false;
    }else if(startTimestamp<0){
      document.getElementById("error").value=bundle.getString("startTimeError");
      return false;
    }else if(endTimestamp<0){
      document.getElementById("error").value=bundle.getString("endTimeError");
      return false;      
    }else if(startTimestamp>endTimestamp){
      document.getElementById("error").value=bundle.getString("timeError");
      return false;      
    }else if((endTimestamp - startTimestamp) >= 60*60*24){
      document.getElementById("error").value = "开始时间到结束时间必须在一天以内";
      return false;
    }

    var retcode={};

    if (dc_type == 0 || dc_type == 6){
      var dc = Ifpms.Xpcom.DCMgmt.createDC(0,ipaddr,pa_num,0,retcode);
    }
    else{
      var dc = Ifpms.Xpcom.DCMgmt.createDC(dc_type,ipaddr,pa_num,0,retcode);
    }
    if (dc_type==0&&retcode.value != 0) {
      document.getElementById("error").value = retcode.value == -1? bundle.getString("invalidIP"):bundle.getString("existedIP");
      return false;
    }
    
    if(dc_type!=0){
      var npa = dc.getPA(1);
      npa.sample_path=logPath;
      npa.sample_startstamp=startTimestamp;
      npa.sample_endstamp=endTimestamp;
      npa.sample_pid=paChannelNum;
    }
    //jsdump('pa new over');
    if( !dc ) {
      document.getElementById("error").value = bundle.getString("unknownError");
      return false;    
    }

    dc.cx = 500;
    dc.cy = 500;

    for (var i=0; i< Ifpms.Xpcom.DCMgmt.pa_list.length; i++) {
      var pa = Ifpms.Xpcom.DCMgmt.pa_list.queryElementAt(i,Components.interfaces.nsIPyIfpmsPA);
      if (pa.did == dc.did) {
        pa.cx = 100 * ( Math.floor((pa.did-1) / 8) ) + pa.pid * 40; 
        pa.cy = 50 * ( (pa.did-1) % 8 + 1);
        window.opener.Ifpms.Map.nodes[pa.sid] = new window.opener.Ifpms.Map.MapNode(pa);
        if (window.opener) {
          var pm = window.opener.Ifpms.PaMgr;
          if (pm) {
            var elt = document.createElement("richlistitem");
            pm.paList.appendChild(elt);
            elt.build(pa);        
          }
        }
      }
    }
    return true;
  },
  domain_new: function domain_new() {

    var dc_type = 5;

    var subnet = document.getElementById("subnet").value;
    var netmask = document.getElementById("netmask").value;
    var deviceNum = document.getElementById("deviceNum").value;

    if(subnet==""){
      document.getElementById("error").value =bundle.getString("invalidIP");
      return false;
    }

    for (var n=0; n<parseInt(deviceNum)*4; n++) {
      var subnet_arr=subnet.split(".",3);
      var ipaddr_n=n+4;
      var ipaddr = subnet_arr.join(".")+"."+ipaddr_n;
      var retcode={};   
      var dc = Ifpms.Xpcom.DCMgmt.createDC(0,ipaddr,2,0,retcode);
      //jsdump("ip: "+ipaddr+", retcode.value: "+retcode.value+", dc: "+dc);
      if ( retcode.value != 0) {
        //document.getElementById("error").value = retcode.value == -1? bundle.getString("invalidIP"):bundle.getString("existedIP");
        //return false;
        continue;
      }
      if( !dc ) {
        //document.getElementById("error").value = bundle.getString("unknownError");
        //return false; 
        continue;  
      }

      dc.protocol_ver = 2;  // v2.0 protocol
      for (var i=0; i< Ifpms.Xpcom.DCMgmt.pa_list.length; i++) {
        var pa = Ifpms.Xpcom.DCMgmt.pa_list.queryElementAt(i,Components.interfaces.nsIPyIfpmsPA);
        jsdump(pa.did +" == "+ dc.did);
        if (pa.did == dc.did) {
          pa.cx = 100 * ( Math.floor((pa.did-1) / 8) ) + pa.pid * 40; 
          pa.cy = 50 * ( (pa.did-1) % 8 + 1);
          window.opener.Ifpms.Map.nodes[pa.sid] = new window.opener.Ifpms.Map.MapNode(pa);
          if (window.opener) {
            var pm = window.opener.Ifpms.PaMgr;
            if (pm) {
              var elt = document.createElement("richlistitem");
              pm.paList.appendChild(elt);
              elt.build(pa);        
            }
          }
        }
      }
      
    }

    return true;
  }
};
