var global_currentusertype = -1; //0 值班员  1 管理员 2超级管理员
var global_currentuseracc = ""; //当前登录用户  账号
var global_loginsuccess=false;
var global_loginfail_time=0;
var global_login_maxtime=5; //最多登录次数
var global_logintime=0;
var global_scrwid=800;
var global_scrhei=600;
var global_alarmlistlength=1000;//保存 最近的 1000条告警记录
var global_wavelayout=2;
var global_wavesetting;
var global_lan='zh-CN';
var global_hlpwindow1=global_hlpwindow1||{};
var global_hlpwindow2=global_hlpwindow2||{};
var global_users=global_users||{};
var global_unpro_alarms=global_unpro_alarms||[];//未处理的告警列表
var global_alarmproc_note='';
var global_alarmproc_win;
var global_alarmproc_mode=1;
var global_alarmwins=[];
global_users.userinfo=[];
global_users.len=global_users.len||0;
var global_configuri='chrome://etc/content/default.conf';
var usermgmt={};
var wavechecked=true;
var alarmSoundtime=3000;
usermgmt.userinfo_uri=Global_GetConfigUri();
function Global_ConfigApp(type) //根据登录的用户类型 进行权限控制
{
//权限控制
var curr_type=global_currentusertype;
$("*[permission]").each(function(){
   if(curr_type<$(this).attr('permission'))//当前用户权限小于 控件要求的最小权限 隐藏此控件
   {
    $(this).hide();
   }
});
$("*[hlpid]").each(function(){
$(this).click(function(){
   Global_openHelpHtml($(this).attr('hlpid'));
});
});
//读取配置中其他信息
var dd = new Date();
var secs=dd.getTime();//
global_logintime=secs;
usermgmt.show_userinfo();
window.setInterval('usermgmt.show_userinfo();',1000*30);
var filepath=GREUtils.File.chromeToPath(usermgmt.userinfo_uri);
var conf= GREUtils.JSON.decodeFromFile(filepath);
//根据 配置文件  设置全局变量 
if(typeof(conf.alarmMax)!='undefined')
{
   global_alarmlistlength=conf.alarmMax;
}
global_wavesetting=conf.wavesetting||[];
document.getElementById('alarmprocmode').value=conf.alarmprocmode||1;
global_alarmproc_mode=conf.alarmprocmode||1;
if(typeof(conf.wavelayout)!='undefined')
{
   global_wavelayout=conf.wavelayout;
}
document.getElementById('sampleNumber').value=conf.wavestart;//波形起点
document.getElementById('sample_end').value=conf.waveend;//波形终点
document.getElementById("image_path").value=conf.mapUrl;//导入map图片路径
document.getElementById("preview").src=conf.mapUrl;
wavechecked=conf.waveChecked;
alarmSoundtime=conf.alarmSoundtime;
//

    document.getElementById("paIcon").value=conf.paIcon;

}
function Global_openHelpHtml(chapter)//打开帮助文档的对应章节
{
       if(!chapter)
       {
          chapter='#';
       }
        var pa={};
        pa.chapterid=chapter;
     	global_hlpwindow1=window.openDialog('chrome://ifpms/content/help.xul','hlpwin1','chrome,resizable=yes,centerscreen,dialog=false',pa); 
        global_hlpwindow1.focus();
}
function Global_GetConfigUri()//获取配置文件路径
{
var defaultconf='chrome://etc/content/default.conf';	
var userfilechromepath="chrome://etc/content/custom.conf";
var userfilepath=GREUtils.File.chromeToPath(userfilechromepath);
if(!GREUtils.File.exists(userfilepath))
{
global_configuri=defaultconf;
}
else{
global_configuri=userfilechromepath;
}
return global_configuri;
}

function verify_user(account, pw) //验证用户账号 密码 
{
	var strbundle = document.getElementById("login_win_str");
	var users1 = get_alluserinfo();
	var res = {};
	var accex=false;
	res.flag = false;
	if(account=='')
	{
	   res.failinfo=strbundle.getString('acc_cannot_be_empty');//'账号为空';
	   return res;
	}
	if(pw=='')
	{
	 res.failinfo=strbundle.getString('pw_cannot_be_empty');//'密码为空';
	 return res;
	}
	for (i = 0; i < users1.length; i++)
	{
		if (users1[i].account == account)
		{
             accex=true;
			if (users1[i].password == GREUtils.CryptoHash.md5(pw))
			{
				res.flag = true;
				res.utype = users1[i].type; // 设置当前 登录用户类型
				res.uacc = account;
			}
			else{
				res.failinfo=strbundle.getString('pwerror');//'密码错误!';
			}
		}
	}
	if(!accex) {
		res.failinfo=strbundle.getFormattedString("accnotexist",[account]);//'用户不存在!';
		}
	return res;
}

function save_alluserinfo(users) // 保存所有用户信息 件中  
{
	global_users.userinfo=users;
}
function update_userinfo(oldacc, userinfo,users) //修改一条用户信息  
{
	var re = {};
	newacc = userinfo.account;
	newpw = userinfo.pw;
	re.succ = false;
	var strbundle = document.getElementById("user_management_str");
        var acc_already_exist=strbundle.getString("accountexistmodifyfail");
	var pwempty=strbundle.getString("emptypwmodifyfail");
	//判断 修改后的用户名是否会重复 
	if (is_account_exist(newacc) && oldacc != newacc) {
		re.des = acc_already_exist;
		return re;
	}
	if (newpw == '') {
		re.des=pwempty;
		return re;
	}
	var vaid=IDnumber_validation(userinfo.idnumber);
	if(!vaid.flag)//
	{		
       re.des=vaid.info;
	   return re;
	}
	var tev=tel_validation(userinfo.tel);
        if(!tev.flag)
        {
            re.des=tev.info;
            return re;
        }
	var up_user = users//;get_alluserinfo();
	for (i = 0; i < up_user.length; i++) {
		if (up_user[i].account == oldacc) //找到对应账号信息
		{
			//原密码和新密码不同 新密码要加密
			if (up_user[i].password != userinfo.password) {
				userinfo.password = GREUtils.CryptoHash.md5(userinfo.password); //	
			}
			up_user[i] = userinfo;
			re.succ = true;
			break;
		}
	}
	var accnotfind=strbundle.getString("failtofindaccount");
	re.des = accnotfind;//"未发现对应账号信息";
	//save_alluserinfo(up_user);
	return re;
}

function get_alluserinfo() //获得所有 用户信息 账号  密码 类型  
{
	if(global_users.userinfo.length==0)
	{
	var ob_userinfo = {}; //保存 用户信息的对象 
	var chromepath =usermgmt.userinfo_uri;//
	var filepath = GREUtils.File.chromeToPath(chromepath); //获取本地文件路径
	var config={};
	try
        {
            config = GREUtils.JSON.decodeFromFile(filepath);
        }
        catch(err)
        {
           config = {};
        }
	ob_userinfo=config['userinfo'];
	global_users.len=ob_userinfo.length;	
	global_users.userinfo=ob_userinfo;
	return ob_userinfo;
       }
       else{
	return global_users.userinfo;
       }
}

function getMapImg(){
    var imgurl=Ifpms.Config.conf['mapUrl'];//读取配置文件
    if(!imgurl){
        imgurl="chrome://ifpms/skin/images/map/default.png";
        Ifpms.Config.conf['mapUrl'] = imgurl;
    }
    return imgurl;
};

function getChecked(){
    var chromepath =usermgmt.userinfo_uri;//
	var filepath = GREUtils.File.chromeToPath(chromepath); //获取本地文件路径
    var config={};
	try
        {
            config = GREUtils.JSON.decodeFromFile(filepath);
        }
    catch(err)
        {
            config = {};
        }
    var checked=config['checked'];//读取配置文件
    return checked;
};

function getPaIcon(){
    var chromepath =usermgmt.userinfo_uri;//
	var filepath = GREUtils.File.chromeToPath(chromepath); //获取本地文件路径
    var config={};
	try
        {
            config = GREUtils.JSON.decodeFromFile(filepath);
        }
    catch(err)
        {
            config = {};
        }
    var paicon=config['paIcon'];//读取配置文件
    if(!paicon){
        paicon=18;
    }
    return paicon;
};

function is_account_exist(acc) //检查 acc是否已经存在
{
	var reg_users = get_alluserinfo();
	for (i = 0; i < reg_users.length; i++) {
		if (reg_users[i].account == acc) {
			return true;
		}
	}
	return false;
}
function delete_userinfo(acc,userlist) //删除一个用户账户信息
{
	var strbundle = document.getElementById("user_management_str");	
	var re = {};
	re.succ = false;
	var users = userlist;//get_alluserinfo();
	for (i = 0; i < users.length; i++) {
		if (acc == users[i].account) {
			users.splice(i, 1); // 删除当前对象
			re.succ = true;
			break;
		}
	}
	if (re.succ == false) {
		var accnotex=strbundle.getFormattedString("accnotexist",[acc]);
		GREUtils.Dialog.alert(strbundle.getString("alert"),accnotex);
	}
	var notfind=strbundle.getFormattedString("cannotfindacc",[acc]);
	re.des =notfind;//"未发现用户:" + acc;
	//save_alluserinfo(users); //将结果保存到文件中
	return re;
}

function get_userinfo_entry(acc) // 获得一个用户的信息  
{
	var userinfos = get_alluserinfo();
	var res = {};
	res.empty = true;
	for (i = 0; i < userinfos.length; i++) {
		if (userinfos[i].account == acc) {
			res.info = userinfos[i];
			res.empty = false;
			return res;
		}
	}
	return res;
}

function do_delete_user() //删除一个用户
{
	var strbundle=document.getElementById("user_management_str");
	var chooseuser=strbundle.getString("choose_acc_to_delete");	
	var olditem = document.getElementById('userinfo_list').selectedIndex;
	if (olditem == -1) {
		GREUtils.Dialog.alert(strbundle.getString("alert"),chooseuser);
		return;
	} else {
		var selecedit = document.getElementById('userinfo_list').childNodes[olditem + 2];
		var item = selecedit.childNodes[0];
		var acc = item.getAttribute('label');
		if (acc == global_currentuseracc) //待删除的账号  正是当前登录的用户
		{
			var cannotdelete=strbundle.getString("cannot_delete_curr_user");
			GREUtils.Dialog.alert(strbundle.getString("alert"),cannotdelete);
			return;
		}
		var params = {};
		params.succ = false;
		params.oldacc = acc; //待删除 id
		//window.openDialog("chrome://ifpms/content/confirm_deleteuser.xul", "", "modal,centerscreen,width=200, height=100", params).focus();
		var strbundle=document.getElementById("user_management_str");
	    var str=strbundle.getFormattedString("confirm_delete_user",[acc]);
		if(GREUtils.Dialog.confirm(strbundle.getString("confirm"),str))
		{
		   var res=delete_userinfo(acc,global_users.userinfo);
		   if(res.succ)
		   {
		    	show_user_list(); // 刷新用户列表
				Ifpms.Config.increase_config();
           }
		   else
		   {
		   }
		}
		else {
		 //	
		}
	}
}

function do_update_selecteduser() //修改选中的用户的信息
{
	var strbundle=document.getElementById("user_management_str");
	var olditem = document.getElementById('userinfo_list').selectedIndex;
	if (olditem == -1) {
		var chooseuser=strbundle.getString("choose_acc_to_modify");
		GREUtils.Dialog.alert(strbundle.getString("alert"),chooseuser);
		return;
	} else {
		var selecedit = document.getElementById('userinfo_list').childNodes[olditem + 2];
		var item = selecedit.childNodes[0];
		var acc = item.getAttribute('label');
		var params = {};
		params.succ = false;
		usinfo = get_userinfo_entry(acc);
		if (usinfo.empty) // 获取用户信息失败
		{
			var cangetuserinfo=strbundle.getString("cannot_get_userinfo");
			GREUtils.Dialog.alert(strbundle.getString("alert"),cangetuserinfo);
			return;
		}
		params.olduserinfo = usinfo.info;
		params.wintype = "modify";
		if (acc == global_currentuseracc) {
			params.typedisabled = true;
		}
		params.global_utype = global_currentusertype;
		params.userlist=global_users.userinfo;
		window.openDialog("chrome://ifpms/content/update_userinfo.xul", "", "centerscreen,modal, width=400, height=400", params).focus();
		if (params.succ) //修改成功
		{
			show_user_list(); // 刷新用户列表
			Ifpms.Config.increase_config();
		}
		if (params.desflag) //修改失败
		{
			//alert(params.des);
		}
	}
}

function show_user_list() //显示用户列表 
{
	var userlist = document.getElementById("userinfo_list");
	var len = userlist.childNodes.length - 2;
	var i = 0;
	for (i = 0; i < len; i++) //....
	{
		userlist.removeChild(userlist.lastChild); // 删除最后一个元素
	}
	var allusers = get_alluserinfo(); //获取所有 用户信息
	if (global_currentusertype == 1) // 一般管理员
	{
		var showusers = [];
		for (i = 0; i < allusers.length; i++) {
			if (allusers[i].type == 0||allusers[i].account==global_currentuseracc) {
				showusers.push(allusers[i]);
			}
		}
		allusers = showusers;
	} else if (global_currentusertype == 0) //值班员只显示自己
	{
		showusers = [];
		for (i = 0; i < allusers.length; i++) {
			if (allusers[i].account == global_currentuseracc) {
				showusers.push(allusers[i]);
				break;
			}
		}
		allusers = showusers;
	}
	var listlen = allusers.length;
	var odd = 0;
	for (i = 0; i < listlen; i++) {
		var listit = document.createElement('listitem');
		if (odd % 2 == 0) {
			//listit.setAttribute("style","background-color:rgb(233,238,236)");
			odd++;
		} else {
			//listit.setAttribute("style","background-color:rgb(233,238,236)");
			odd++;
		}
		var strbundle=document.getElementById("user_management_str");
		var online=strbundle.getString("online");
		var offline=strbundle.getString("offline");		
		var acc = allusers[i].account;
		var state = offline;
		if (acc == global_currentuseracc) {
			state = online;
			listit.setAttribute("style", "background-color:rgb(220,245,220)");
		}
		var type = allusers[i].type;
		
		var attendant=strbundle.getString("attendant");
		var admin=strbundle.getString("admin");
		var superad=strbundle.getString("super");
		
		if (type == '0') {
			type =attendant;
		} else if (type == '1') {
			type = admin;
		} else {
			type = superad;
		}
		var gender = allusers[i].gender;
		var ma=strbundle.getString("male");
		var fe=strbundle.getString("female");
		if (gender == '0') {
			gender = ma;
		} else {
			gender = fe;
		}
		var name = allusers[i].name;
		var userin = [];
		userin.push(acc, state, type, name, gender);
		for (var j = 0; j < 5; j++) {
			var listce = document.createElement("listcell");
			listce.setAttribute("label", userin[j]);
			listit.appendChild(listce);
		}
		document.getElementById("userinfo_list").appendChild(listit);
	}
}
usermgmt.show_userinfo=function()
{
var strbun=document.getElementById('main_str');
var infostr=strbun.getString('curuser');//'当前用户:';
infostr="";
switch(global_currentusertype)
{
	case '0':infostr+=strbun.getString('attendant');break;
	case '1':infostr+=strbun.getString('admin');break;
	case '2':infostr+=strbun.getString('super');break;
	default:infostr+=strbun.getString('attendant');
};
   infostr+=":"+global_currentuseracc;
   document.getElementById('userinfo').value=infostr;//  
   infostr=''+strbun.getString('logged');//"  已登录: ";
   var dd = new Date();
   var now=dd.getTime();//
   var diff=(now-global_logintime)/1000/60;
   diff=Math.floor(diff);
   infostr+=diff+' '+strbun.getString('mins');
   document.getElementById('onlinetime').value=infostr;
}

function Global_SaveUserConfig()//保存用户配置信息
{
}

//格式化时间
Date.prototype.format = function(format){ 
var o = { 
"M+" : this.getMonth()+1, //month 
"d+" : this.getDate(), //day 
"h+" : this.getHours(), //hour 
"m+" : this.getMinutes(), //minute 
"s+" : this.getSeconds(), //second 
"q+" : Math.floor((this.getMonth()+3)/3), //quarter 
"S" : this.getMilliseconds() //millisecond 
} 

if(/(y+)/.test(format)) { 
format = format.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length)); 
} 

for(var k in o) { 
if(new RegExp("("+ k +")").test(format)) { 
format = format.replace(RegExp.$1, RegExp.$1.length==1 ? o[k] : ("00"+ o[k]).substr((""+ o[k]).length)); 
} 
} 
return format; 
} 

function  global_CheckSound()//检查是否有 未处理的 告警
{

   if(global_unpro_alarms.length>0)
   {
        GREUtils.Sound.play("chrome://ifpms/content/media/warn.wav"); 
   }

}

function Global_SaveAlarmlist()//
{
var chromepath="chrome://etc/content/alarm.log";
var filepath=GREUtils.File.chromeToPath(chromepath);
var alarmlist=[];
if(!GREUtils.File.exists(filepath))//文件不存在
{	  
	GREUtils.Dir.getFile(filepath);//创建文件
}
//
var start=Ifpms.Xpcom.DCMgmt.alarm_history.length-global_alarmlistlength;
start=start>0?start:0;
for(var i=start;i<Ifpms.Xpcom.DCMgmt.alarm_history.length;i++)
{
	  var alarm=Ifpms.Xpcom.DCMgmt.alarm_history.queryElementAt(i,Components.interfaces.nsIPyIfpmsAlarmRecord);
      var foo={};
	  var ids=['id','aid','did','pid','happen_time','notes','is_confirmed','confirm_notes','confirm_time','confirm_operator'];
      for(var j in ids)
	  {
	    foo[ids[j]]=alarm[ids[j]];
	  }
	  foo.happenlocaltime=new Date(parseInt(foo.happen_time) * 1000).format("yyyy-MM-dd hh:mm:ss ");//
	  foo.confirmlocaltime=new Date(parseInt(foo.confirm_time)*1000).format("yyyy-MM-dd hh:mm:ss ");

	  if (Ifpms.Xpcom.DCMgmt.dc_list.length>=2 &&Ifpms.Xpcom.DCMgmt.getDC(2)!=null){
		  var pa=Ifpms.Xpcom.DCMgmt.getDC(2).getPA(2);
		  if(foo.did == 2 && foo.pid == 2 && foo.aid == 4 && pa.work_mode==2){
		  	foo.aid = 9;
		  }
		  else if(foo.did == 2 && foo.pid == 2 && foo.aid == 2 && pa.work_mode==2){
		  	foo.aid = 10;
		  }
		}
	  alarmlist.push(foo);
}
    alarmlist.reverse();
	GREUtils.JSON.encodeToFile(filepath,alarmlist);	
}

function getCurrentSysPath(){
    var skinHref="chrome://ifpms/skin";
    skinHref=GREUtils.File.chromeToPath(skinHref);
    skinHref=skinHref.replace(/\\/g, "/");
    var skinName=skinHref.substring(skinHref.lastIndexOf("/")+1,skinHref.length);
    return skinName;
}
