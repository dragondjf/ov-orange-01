var sysmgmt={};
sysmgmt.landesc={
    "zh-CN":"中文简体",
    "zh-TW":"中文繁体",
    "en-US":"English(American)"
}
sysmgmt.ini=function()
{
    var lans=Global_GetLangs();//获得所有支持语言 
    var lanpopup=document.getElementById('sys_lan');
    for (var j=lanpopup.childNodes.length-1;j>=0;j--)
    {
        lanpopup.removeChild(lanpopup.childNodes[j]);
    }
    for(var i=0;i<lans.length;i++)
    {
       var item=document.createElement('menuitem');
       
       item.setAttribute('value',lans[i]);
       item.setAttribute('label',sysmgmt.landesc[lans[i]]);
       lanpopup.appendChild(item);
    }
   var prefs = Components.classes["@mozilla.org/preferences-service;1"].
   getService(Components.interfaces.nsIPrefBranch);
   global_lan=prefs.getCharPref("general.useragent.locale");
   document.getElementById('sys_menulistlan').value=global_lan;
   document.getElementById('sys_alarmmax').value=global_alarmlistlength;
}

//获取选择图片本地路径，小图预览
function update_image(){
  var constrs=document.getElementById("sys_management_str");
  var file_url = document.getElementById("image_path").value;
  
  if(file_url == undefined || file_url.length == 0){
    GREUtils.Dialog.alert(constrs.getString("alert"),constrs.getString("selectImg"));
    oncancel();
    return;
  } else {
    var t =file_url.replace(/\\/g, "/");
    var t_filename=t.substring(t.lastIndexOf("/")+1,t.length);
    if(!t_filename.match(/.jpg|.png/i )){
      GREUtils.Dialog.alert(constrs.getString("alert"),constrs.getString("pathType"));
      oncancel();
      return;
    } else {
      document.getElementById("preview").setAttribute("src","file://"+file_url);
    }
  }

}

//取消导入
function oncancel(){
  document.getElementById("preview").setAttribute("src",Ifpms.Config.mapUrl);
  document.getElementById("image_path").value=Ifpms.Config.mapUrl;
}

function UseDefaultImg(){
    document.getElementById("image_path").value="chrome://ifpms/skin/images/map/default.png";
    document.getElementById("preview").src="chrome://ifpms/skin/images/map/default.png";
}


//最终确认，将图片从本地文件复制到项目文件
function get_selected_image_url(){

  var file_url = document.getElementById("image_path").value;
  if (file_url != Ifpms.Config.mapUrl) {
    if (/^chrome:/.test(file_url)) {
      return file_url;
    } else {
      //GREUtils.File.remove(userfilepath);//删除文件
      var t_url=file_url.replace(/\\/g, "/");
      var t_filename=t_url.substring(t_url.lastIndexOf("/")+1,t_url.length);
      GREUtils.File.copy(file_url,GREUtils.File.chromeToPath("chrome://mapImg/content"));//复制
      return "chrome://mapImg/content/" + t_filename;
    }
  } else {
    return file_url;
  }

  window.clearInterval(window.ifpms_autosave_timer);
  Ifpms.Config.increase_config();
  Ifpms.Config.save();

  let appStartup = Components.classes['@mozilla.org/toolkit/app-startup;1']
                         .getService(Components.interfaces.nsIAppStartup);                               
  appStartup.quit(Components.interfaces.nsIAppStartup.eAttemptQuit |
                         Components.interfaces.nsIAppStartup.eRestart);

/*
  var userfilechromepath="chrome://mapImg/content/"+subPath;
  var userfilepath=GREUtils.File.chromeToPath(userfilechromepath);
  //alert(userfilepath);
  var aPaths=
  var file_url = document.getElementById("image_path").value;
  var subPathType=file_url.substring(file_url.lastIndexOf("."),file_url.length);  
  if(file_url==""){
    GREUtils.Dialog.alert(constrs.getString("alert"),constrs.getString("selectImg"));
    return;
  }else if(!subPathType.match(/.jpg|.png/i )){
    GREUtils.Dialog.alert(constrs.getString("alert"),constrs.getString("pathType"));
    oncancel();
    return;
  }else if(GREUtils.File.exists(userfilepath)){	  
    //文件是否存在
    GREUtils.File.remove(userfilepath);//删除文件
  }
  GREUtils.File.copy(file_url,aPaths);//复制
  Global_MapImg();
*/
}

//获得所选图片的chrome路径
function getMapImgURL(){
  var file_url = document.getElementById("image_path").value;
  file_url=file_url.replace(/\\/g, "/");
  var chromePath="chrome://mapImg/content/";
  var subPath=file_url.substring(file_url.lastIndexOf("/")+1,file_url.length);
  var imgURL="chrome://ifpms/skin/images/map/default.png";
  if(subPath=="undefined"||file_url==imgURL){
    return imgURL;
  }
  if(file_url!=""){
    imgURL=chromePath+subPath;
  }
  return imgURL;
}

function getPaIconArray(){
    var paIconVal=document.getElementById("paIcon").value;
    return paIconVal;    
}

function OnSwitchLan(lang)
{
  if(lang!=global_lan)
	{
              // global_lan=lang;
	      Global_SwitchToLan(lang);
	}
}

function SavePaIcon(){

  if(Ifpms.Config.conf.paIcon == document.getElementById("paIcon").value) {
    //设置无变更
    return;
  } else {
    var bundle=document.getElementById("sys_management_str");
    var constr=bundle.getString("restartPaIcon");
    if(GREUtils.Dialog.confirm(bundle.getString("confirm"),constr)){
      //保存设置
      window.clearInterval(window.ifpms_autosave_timer);
      Ifpms.Config.increase_config();
      Ifpms.Config.save();
      //重新启动 
      let appStartup = Components.classes['@mozilla.org/toolkit/app-startup;1']
                             .getService(Components.interfaces.nsIAppStartup);                               
      appStartup.quit(Components.interfaces.nsIAppStartup.eAttemptQuit |
                             Components.interfaces.nsIAppStartup.eRestart);
    }else{
      document.getElementById("paIcon").value=Ifpms.Config.conf.paIcon;
    }    
  }

}

function Global_SwitchToLan(lang)
{       
       var lanname=sysmgmt.landesc[lang];//
       var bundle=document.getElementById("sys_management_str");
       var constr=bundle.getFormattedString('restartprompt',[lanname]);
       if(GREUtils.Dialog.confirm(bundle.getString("confirm"),constr))
       {
          var prefs = Components.classes["@mozilla.org/preferences-service;1"].
          getService(Components.interfaces.nsIPrefBranch);
          

          window.clearInterval(window.ifpms_autosave_timer);
          Ifpms.Config.mapUrl = get_selected_image_url();
          Ifpms.Config.paIcon = getPaIconArray();
          Ifpms.Config.increase_config();
          Ifpms.Config.save();

          prefs.setCharPref("general.useragent.locale",lang);        
          
          //重新启动 
          var appStartup = Components.classes['@mozilla.org/toolkit/app-startup;1']
                                 .getService(Components.interfaces.nsIAppStartup);                               
          appStartup.quit(Components.interfaces.nsIAppStartup.eAttemptQuit |
                                 Components.interfaces.nsIAppStartup.eRestart);
       }else{
//         prefs.setCharPref("general.useragent.locale",global_lan);        
         document.getElementById("sys_menulistlan").value = global_lan;
       }
}

function Global_MapImg(){
    var bundle=document.getElementById("sys_management_str");
    var constr=bundle.getString("restartMapImg");
    if(GREUtils.Dialog.confirm(bundle.getString("confirm"),constr)){
        var savestr=document.getElementById("sys_management_str").getString('saveconfigprompt');
//        if(GREUtils.Dialog.confirm(bundle.getString("confirm"),savestr)){
          window.clearInterval(window.ifpms_autosave_timer);
          Ifpms.Config.increase_config();
          Ifpms.Config.save();
//        }
        //重新启动 
        let appStartup = Components.classes['@mozilla.org/toolkit/app-startup;1']
                               .getService(Components.interfaces.nsIAppStartup);                               
          appStartup.quit(Components.interfaces.nsIAppStartup.eAttemptQuit |
                               Components.interfaces.nsIAppStartup.eRestart);
    }
    else{
      oncancel();
    }
}

function Global_GetLangs()//get all languages installed in application. 
{
    var  ret=[];
	var chromeRegService = Components.classes["@mozilla.org/chrome/chrome-registry;1"].getService();
	var xulChromeReg = chromeRegService.QueryInterface(Components.interfaces.nsIXULChromeRegistry);
	var toolkitChromeReg = chromeRegService.QueryInterface(Components.interfaces.nsIToolkitChromeRegistry);
	var selectedLocale = xulChromeReg.getSelectedLocale("ifpms");
	var availableLocales = toolkitChromeReg.getLocalesForPackage("ifpms");        
        while(availableLocales.hasMore()) {
		var locale = availableLocales.getNext();
                ret.push(locale);
	}
    return ret;
}
