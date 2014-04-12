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
function getValue(){
  var file_url = document.getElementById("update_image").value;
  var img=document.getElementById("preview");
  img.setAttribute("src","file://"+file_url);
}

//取消导入
function oncancel(){
  var img=document.getElementById("preview");
  img.setAttribute("src",getMapImg());
  document.getElementById("update_image").value=getMapImg();
}

function UseDefaultImg(){
    document.getElementById("update_image").value="chrome://ifpms/skin/images/map/default.png";
    document.getElementById("preview").src="chrome://ifpms/skin/images/map/default.png";
    sub();
}

//将图片从本地文件复制到项目文件
function sub(){
  var constrs=document.getElementById("sys_management_str");
  var file_url = document.getElementById("update_image").value;
  file_url=file_url.replace(/\\/g, "/");
  var subPath=file_url.substring(file_url.lastIndexOf("/")+1,file_url.length);
  var userfilechromepath="chrome://mapImg/content/"+subPath;
  var userfilepath=GREUtils.File.chromeToPath(userfilechromepath);
  //alert(userfilepath);
  var aPaths=GREUtils.File.chromeToPath("chrome://mapImg/content");
  var file_url = document.getElementById("update_image").value;
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
}

//获得所选图片的chrome路径
function getMapImgURL(){
  var file_url = document.getElementById("update_image").value;
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
    getPaIconArray();
    var bundle=document.getElementById("sys_management_str");
    var constr=bundle.getString("restartPaIcon");
    if(GREUtils.Dialog.confirm(bundle.getString("confirm"),constr)){
        var savestr=document.getElementById("sys_management_str").getString('saveconfigprompt');
        if(GREUtils.Dialog.confirm(bundle.getString("confirm"),savestr)){
            Global_SaveUserConfig();//保存系统配置            
        }
        //重新启动 
        let appStartup = Components.classes['@mozilla.org/toolkit/app-startup;1']
                               .getService(Components.interfaces.nsIAppStartup);                               
          appStartup.quit(Components.interfaces.nsIAppStartup.eAttemptQuit |
                               Components.interfaces.nsIAppStartup.eRestart);
    }else{
      document.getElementById("paIcon").value=getPaIcon();
    }
}

function Global_SwitchToLan(lang)
{       
        var prefs = Components.classes["@mozilla.org/preferences-service;1"].
        getService(Components.interfaces.nsIPrefBranch);
        prefs.setCharPref("general.useragent.locale",lang);        
       var lanname=sysmgmt.landesc[lang];//
       var bundle=document.getElementById("sys_management_str");
       var constr=bundle.getFormattedString('restartprompt',[lanname]);
       if(GREUtils.Dialog.confirm(bundle.getString("confirm"),constr))
       {
          var savestr=document.getElementById("sys_management_str").getString('saveconfigprompt');
          if(GREUtils.Dialog.confirm(bundle.getString("confirm"),savestr))
          {
             Global_SaveUserConfig();//保存配置
          }
        //重新启动 
        var appStartup = Components.classes['@mozilla.org/toolkit/app-startup;1']
                               .getService(Components.interfaces.nsIAppStartup);                               
          appStartup.quit(Components.interfaces.nsIAppStartup.eAttemptQuit |
                               Components.interfaces.nsIAppStartup.eRestart);
       }else{
         document.getElementById("sys_menulistlan").value = global_lan;
       }
}

function Global_MapImg(){
    var bundle=document.getElementById("sys_management_str");
    var constr=bundle.getString("restartMapImg");
    if(GREUtils.Dialog.confirm(bundle.getString("confirm"),constr)){
        var savestr=document.getElementById("sys_management_str").getString('saveconfigprompt');
        if(GREUtils.Dialog.confirm(bundle.getString("confirm"),savestr)){
            Global_SaveUserConfig();//保存系统配置            
        }
        //重新启动 
        let appStartup = Components.classes['@mozilla.org/toolkit/app-startup;1']
                               .getService(Components.interfaces.nsIAppStartup);                               
          appStartup.quit(Components.interfaces.nsIAppStartup.eAttemptQuit |
                               Components.interfaces.nsIAppStartup.eRestart);
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
