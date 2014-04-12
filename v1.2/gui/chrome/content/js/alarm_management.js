var alarmmgmt={};
//装载 历史告警记录 
(function(){
var chromepath="chrome://etc/content/alarm.log";
var filepath=GREUtils.File.chromeToPath(chromepath);
try 
{
if(!GREUtils.File.exists(filepath))//文件不存在
{	  
   alarmli=[];
}
else{
   var alarmli=GREUtils.JSON.decodeFromFile(filepath);
}
}  
catch(err)
{
 //alert('load file error');
 alarmli=[];
}
if(alarmli.length>0)
{
  alarmli.reverse();
}
for(var i in alarmli)
{
    Ifpms.Xpcom.DCMgmt.newAlarm(alarmli[i].did,alarmli[i].pid,alarmli[i].aid, true, false);
	var ids=['id','happen_time','notes','is_confirmed','confirm_notes','confirm_time','confirm_operator'];
	var nalarm=Ifpms.Xpcom.DCMgmt.alarm_history.queryElementAt(Ifpms.Xpcom.DCMgmt.alarm_history.length-1,Components.interfaces.nsIPyIfpmsAlarmRecord);
    for(var j in ids)
	{
	   nalarm[ids[j]]=alarmli[i][ids[j]];
	}
}
})();
alarmmgmt.ini=function()
{
this.tablemanager.ini();
}
alarmmgmt.typeinfo=['禁用','断开','运行','预警','告警', '断纤', '爆破','拆盖','机盖正常','风雨','启动'];
var lanprefs = Components.classes["@mozilla.org/preferences-service;1"].
   getService(Components.interfaces.nsIPrefBranch);
var lan=lanprefs.getCharPref("general.useragent.locale");
if(lan=='en-US'){
 alarmmgmt.typeinfo=['Disable','Disconnect','Running','Prewarn','Alarm', 'Break', 'Blast','Lid-open','Lid-close'];
}
alarmmgmt.styles=[//01  告警类型1 已确认,  00 告警类型1 未确认, 11 告警类型2已确认, 10告警类型2未确认
    {'background':'#ffeded'}, //00 告警类型1未确认 0 
    {'background':'#eeffee'},// 01告警类型1已确认  1
    {'background':'#ffefef'},//10告警类型2未确认   2
    {'background':'#eeffff'},//11 告警类型2已确认  3
    {'background':'#faeefd'},//100 告警类型3未确认 4
    {'background':'#ffeefa'}, //101 告警3 已确认    5
    {'background':'#faeefd'},//110  告警4 未确认  6
    {'background':'#faeefd'},//111 告警4 已确认  7
    {'background':'#303030'}//1000
];
alarmmgmt.tablemanager={
'listlength':Ifpms.Xpcom.DCMgmt.alarm_history.length,
'list':[],
'newestAlarm':[],
'pages':0,
'pagesize':20,
'currentpage':0 ,
'alarm_start':Ifpms.Xpcom.DCMgmt.alarm_history.length-20,
'alarm_end':Ifpms.Xpcom.DCMgmt.alarm_history.length,
'getAlarmlist':function(va)
{
    this.list.splice(0,this.list.length);
    jsdump("getalarmlist: "+this.alarm_start+"-"+this.alarm_end);
    if(this.alarm_start < 0){
      this.alarm_start = 0;
    }
    for(var i=parseInt(this.alarm_start);i<parseInt(this.alarm_end);i++)
     {  
         var alarm=Ifpms.Xpcom.DCMgmt.alarm_history.queryElementAt(i,Components.interfaces.nsIPyIfpmsAlarmRecord);
        // if(alarm.did == 2 && alarm.pid == 2 && alarm.aid == 4 ){
        //   alarm.aid = 9;
        // }
        // else if(alarm.did == 2 && alarm.pid == 2 && alarm.aid == 2){
        //   alarm.aid = 10;
        // }
         // if(va==4){
         //    if(alarm.aid>=va && alarm.aid!=8 && alarm.aid != 10){
         //        this.list.push(alarm);
         //    }
         // }else if(va==0){
         //    this.list.push(alarm);
         // }
         var paname = Ifpms.Xpcom.DCMgmt.getDC(alarm.did).getPA(alarm.pid).name;
         if (paname != "环境自适应探测器"){
          this.list.push(alarm);
         }
     }
     alarmmgmt.sortList('happen_time',this.list,1);
     // this.listlength=Ifpms.Xpcom.DCMgmt.alarm_history.length;
     if(this.pagesize==0)
     {
        this.pages=0;
     }
     else{
        this.pages=Math.ceil(this.listlength/this.pagesize);
     }
     this.currentpage=this.currentpage||1;
},
'nextPage':function()
{
      this.currentpage=this.currentpage>this.pages-1?this.pages:++this.currentpage;
      if(this.alarm_start == 0){
        return;
      }
      this.alarm_start -= this.pagesize;
      this.alarm_end -= this.pagesize;
      this.alarm_start = this.alarm_start<0?0:this.alarm_start;
      jsdump("next: "+this.alarm_start+","+this.alarm_end);
      this.showCurrentPage();
},
'previewPage':function()
{
    this.currentpage=this.currentpage-1<1?1:this.currentpage-1;
    if(this.alarm_end == this.listlength){
      return;
    }
    this.alarm_start = parseInt(this.alarm_start);
    this.alarm_end = parseInt(this.alarm_end);
    if(this.alarm_end < this.pagesize){
      this.alarm_start += this.alarm_end;
    }else{
      this.alarm_start += parseInt(this.pagesize);
    }
    this.alarm_end += parseInt(this.pagesize);
    jsdump("prev: "+this.alarm_start+","+this.alarm_end);
    this.showCurrentPage();
},
'showCurrentPage':function()
{
    var alarm_body=$('#alarm_table_body');
    alarm_body.empty();
    //var start=(this.currentpage-1)*this.pagesize;
    var strbun=document.getElementById('alarm_str');
    this.getAlarmlist();
    // if(this.list.length==0) { return ;}
    for(var i=0;i<this.list.length;i++)
    {
        //if(start+i>=this.listlength) {break;}
        var styleinx=0;
        var tr=document.createElementNS('http://www.w3.org/1999/xhtml','html:tr');
        //var foo=start+i;
		    //jsdump(this.list);
        var td1=alarmmgmt.makeTD(this.list[i].id);//
        tr.appendChild(td1);
        var alarmtypestr=alarmmgmt.typeinfo[this.list[i].aid];
        var td2=alarmmgmt.makeTD(alarmtypestr);
        styleinx=convertDecimalToBin(this.list[i].aid);//告警类型（0，1）=>(1,2) (con,uncon->(1,0)) 
        //styleinx=parseInt(this.list[start+i].aid,2);
        tr.appendChild(td2);
        
        var td3=alarmmgmt.makeTD(this.list[i].did);
        if (this.list[i].aid == 7 || this.list[i].aid == 8){
          td3=alarmmgmt.makeTD("---");
        }
        tr.appendChild(td3);
        var td4=alarmmgmt.makeTD(this.list[i].pid);
        if (this.list[i].aid == 7 || this.list[i].aid == 8){
          td4=alarmmgmt.makeTD("---");
        }
        tr.appendChild(td4);

        var strtime=new Date(parseInt(this.list[i].happen_time) * 1000).toLocaleString();//
        var td5=alarmmgmt.makeTD(strtime);
        tr.appendChild(td5);
        var tdplay=document.createElementNS("http://www.w3.org/1999/xhtml","html:td");
        var playwav=strbun.getString('play');
        var play=document.createElementNS("http://www.w3.org/1999/xhtml","html:input");
	      var confirmed=strbun.getString('confirmed');
	      var unconfirmed=strbun.getString('unconfirmed');	
        var confirmstr=this.list[i].is_confirmed?confirmed:unconfirmed;
	      styleinx=10*parseInt(styleinx);
        styleinx=0;
        styleinx=this.list[i].is_confirmed?styleinx+1:styleinx+0;
	      styleinx=convertBinToDecimal(styleinx); 
	      if(styleinx>alarmmgmt.styles.length-1)
	      {
            styleinx=alarmmgmt.styles.length-1;
	      }
        var td6=alarmmgmt.makeTD(confirmstr);
        tdplay.setAttribute("width","5%");
        tdplay.setAttribute("align","center");
        var tdnote=document.createElementNS("http://www.w3.org/1999/xhtml","html:td");
        tdnote.setAttribute('align','center');
        var tdnote_label=document.createElement('label');//
        tdnote_label.setAttribute('value',this.list[i].confirm_notes);
        tdnote.appendChild(tdnote_label);
        //tdnote.setAttribute('status','input');
        play.setAttribute("type","button");
        play.setAttribute("width","20");
        play.setAttribute("value",playwav);
        if(this.list[i].aid >= 7){
          play.setAttribute("disabled","disabled");
          //play.setAttribute("did",0);
          //play.setAttribute("pid",0);
        }else{
          play.setAttribute("alarmsId",this.list[i].id);
          play.setAttribute("aid",alarmtypestr);
          play.setAttribute("did",this.list[i].did);
          play.setAttribute("pid",this.list[i].pid);
          play.setAttribute("time",this.list[i].happen_time);
          play.setAttribute("confirmstr",confirmstr);
          play.setAttribute("note",tdnote_label.getAttribute("value"));
        }
        tdplay.appendChild(play);
        tr.appendChild(td6);
        tr.appendChild(tdplay);
        if(!this.list[i].is_confirmed)
        {
            var tdtext=document.createElementNS("http://www.w3.org/1999/xhtml","html:input");
            tdtext.setAttribute('type','text');
            tdtext.setAttribute('maxlength','40');
            tdtext.setAttribute('confirm_note_assoid',this.list[i].id);
            tdnote.appendChild(tdtext);
            tdnote.setAttribute('status','input');
            this.shiftConfirmNotes(tdnote);
        }
        tr.appendChild(tdnote);
        var strcontime;
        if(this.list[i].confirm_time!=0)
        {
          strcontime=new Date(parseInt(this.list[i].confirm_time)*1000).toLocaleString();//
        }
        else{
          strcontime='---';
        }
        var td7=alarmmgmt.makeTD(strcontime);
        tr.appendChild(td7);
		    var td9=alarmmgmt.makeTD(this.list[i]['confirm_operator']);
        tr.appendChild(td9);
        var td8=document.createElementNS("http://www.w3.org/1999/xhtml","html:td");
        td8.setAttribute('align','center');
        var inp=document.createElement('checkbox');
        inp.setAttribute('checked','false');
        inp.setAttribute('confirmed','yes');
        inp.setAttribute('check_alarmid',this.list[i].id);
        if(!this.list[i].is_confirmed)
        {            
            inp.setAttribute('confirmed','no');
        }
        if(typeof(alarmmgmt.styles[styleinx])=='undefined')
        {
            jsdump('Error style index  is : '+styleinx);
        }
        tr.style.backgroundColor=alarmmgmt.styles[styleinx].background;
        td8.appendChild(inp);
        tr.appendChild(td8);

        $("#alarm_table_body").append(tr);
    }
    document.getElementById("check_alarm").checked=false;
    var str=strbun.getFormattedString('pageinfo',[this.listlength,this.pagesize,this.currentpage,this.pages]);
    $('#alarm_table_foot').attr('value',str);
    document.getElementById('alarm_desc_page').value=this.currentpage;
    document.getElementById('alarm_confirm').setAttribute('label',strbun.getString('confirmalarm'));
    document.getElementById('alarm_confirm').setAttribute('status','showmode');
},
'showNewestAlarm':function(){
    this.getAlarmlist(4);
    alarmmgmt.sortList('happen_time',this.list,1);
    this.newestAlarm = this.list.slice(0,5);
    this.newestAlarmInit(5);
},
'newestAlarmInit':function(size){
    $("#index_alarm_body").empty();
    // jsdump("----------length--------------:"+this.newestAlarm.length);
    size=size<this.newestAlarm.length?size:this.newestAlarm.length;
    for(var i=0; i<size; i++){
       var tr=document.createElementNS("http://www.w3.org/1999/xhtml","html:tr");
       var alarmid=this.newestAlarm[i].aid;
       var alarmtype=alarmmgmt.typeinfo[this.newestAlarm[i].aid];
       var td1=alarmmgmt.makeTD(alarmtype);
       var did=this.newestAlarm[i].did;
       var pid=this.newestAlarm[i].pid;
       var pa;
       var name;
       if(did!=0&&pid!=0){
          pa=Ifpms.Xpcom.DCMgmt.getDC(did).getPA(pid);
          name=pa.name;
       }else{
          name="---";
       }       
       var td2=alarmmgmt.makeTD(name);
       var strTime=new Date(parseInt(this.newestAlarm[i].happen_time)*1000).toLocaleString();
       var td3=alarmmgmt.makeTD(strTime);
       tr.appendChild(td1);
       tr.appendChild(td2);
       tr.appendChild(td3);
       $("#index_alarm_body").append(tr);
       alarmid = parseInt(alarmid);
       switch(alarmid){
        case 2:
            td1.style.background="#6fff6f";
            td1.style.fontWeight="bold";
            td1.style.color="#000";
            break;
        case 3:
        case 5:
            td1.style.background="#FFFF00";
            td1.style.fontWeight="bold";
            td1.style.color="#000";
            break;
        case 4:
        case 6:
            td1.style.background="#ff0000";
            td1.style.fontWeight="bold";
            td1.style.color="#000";
            break;
       }
       
    }
},
'showAudio':function(alarmInfo){
    Ifpms.PaMgr.openDialog("chrome://ifpms/content/showAudio.xul",alarmInfo);
},

'shiftConfirmNotes':function(td)
{
    if(td.getAttribute('status')=='label')
    {
        td.childNodes[0].style.display='none';
        td.childNodes[1].style.display='';
    }
    else{
        td.childNodes[1].style.display='none';
        td.childNodes[0].style.display='';
    }
},
'filterTable':function(va)
{
//jsdump('alarm record filter value: '+va);
//this.getAlarmlist(va);
this.ini(va);
}
, 
'ini':function(v)
{
 //    var type=document.getElementById('alarmfilter').value;
	// if(typeof(v)!='undefined')
	// {
	//   type=v;
	// }
    //this.getAlarmlist();//只显示吿警以上 级别信息
    this.listlength=Ifpms.Xpcom.DCMgmt.alarm_history.length;
    var strbun=document.getElementById('alarm_str');
    if(this.listlength==0)//没有告警
    {
        document.getElementById('alarmtable').style.display='none';
        document.getElementById('alarm_controlbar').style.display='none';
        document.getElementById('alarm_table_title').setAttribute('value',strbun.getString('alarmlistnull'));
        // return;
    }
    else{
        document.getElementById('alarmtable').style.display='';
        document.getElementById('alarm_controlbar').style.display='';
        document.getElementById('alarm_table_title').setAttribute('value','');
    }
    // var oldpagesize=document.getElementById('alarmpagesize').value=20;
    // this.pagesize=oldpagesize;
    this.pages=Math.ceil(this.listlength/this.pagesize);
    if(this.currentpage<1||this.currentpage>this.pages)
    {
        this.currentpage=1;
    }
    this.redrawTable();
},
'selectAll':function()
{
      var va=document.getElementById("check_alarm").checked;
      if(va==false)
      {
       $("[check_alarmid]").attr('checked',true);
      }
      else{
       $("[check_alarmid]").attr('checked',false);
      }
},
'getSelectedID':function()
{
    var slist=[];
    $("[check_alarmid]:checked").each(function(){
                slist.push($(this).attr('check_alarmid'));             
    });
    return slist;
},
'getUnconfirmSelectedID':function()
{
    var slist=[];
    $("[confirmed=no]:checked").each(function(){
                slist.push($(this).attr('check_alarmid'));             
    });
    return slist;
},
'removeSelectedAlarms':function()
{
    var strbun=document.getElementById('alarm_str');
    var ali=this.getSelectedID();
    if(ali.length==0)
    {
        GREUtils.Dialog.alert(strbun.getString('alert'),strbun.getString('chooserecordtoclear'));
        return;
    }
    if(!GREUtils.Dialog.confirm(strbun.getString('confirm'),strbun.getString('confirmremove')))
    {
        return;
    }
    var rmindex;
    for(var i=0;i<ali.length;i++)
    {
        rmindex=alarmmgmt.getIndexByID(ali[i]);
		if(rmindex==-1)
        {
            jsdump('item does not exist');
        }
        else{
            Ifpms.Xpcom.DCMgmt.alarm_history.removeElementAt(rmindex);
			
			for(var j in global_unpro_alarms)//未处理的吿警中删除对应条目  
	        {
	          if(global_unpro_alarms[j].alarmid==ali[i])
	          {
		         global_unpro_alarms.splice(j,1);
		      }
	        }
	       for(var j in global_alarmwins)//关闭可能打开的 吿警处理对话框
	       {
		      //jsdump(global_alarmwins[j].toString());
			  if(typeof(global_alarmwins[j].alarm)=='undefined'){ continue;}
	          if(global_alarmwins[j].alarm.alarmid==ali[i])
	          {
	             global_alarmwins[j].close();
	             global_alarmwins.splice(j,1);
	          }
	      }
        }
    }    
    this.ini();//重新加载
    //mgmt.ini();
    this.showNewestAlarm();
},
'onConfirmSelectedAlarms':function()
{
    var strbun=document.getElementById('alarm_str');
    if(document.getElementById('alarm_confirm').getAttribute('status')=='showmode')
    {
     var list=this.getUnconfirmSelectedID();   
        if(list.length==0)
        {
            GREUtils.Dialog.alert(strbun.getString('alert'),strbun.getString('chooserecordtoconfirm'));
            return;
        }      
    document.getElementById('alarm_confirm').setAttribute('label',strbun.getString('commitrecord'));      
    for(var i in list )
    {
       $("[confirm_note_assoid="+list[i]+"]").each(function(){
        $(this).css('display','');
        $(this).prev().css('display','none');
        });
    }
    document.getElementById('alarm_confirm').setAttribute('status','editmode');
    }
    else{
        document.getElementById('alarm_confirm').setAttribute('label',strbun.getString('confirmalarm'));
        document.getElementById('alarm_confirm').setAttribute('status','showmode');
         var list=this.getUnconfirmSelectedID();
        for(var i in list )
        {
          $("[confirm_note_assoid="+list[i]+"]").each(function(){
          alarmmgmt.tablemanager.doConfirmAlarmRecord(list[i],$(this).val());
          });
        }
     this.showCurrentPage();//  
    }
},
'doConfirmAlarmRecord':function(id,notes)
{
    var index=alarmmgmt.getIndexByID(id);
    if(index==-1){jsdump('Alarm does not exist');return;}
    //var alarm=Ifpms.Xpcom.DCMgmt.alarm_history.queryElementAt(index,Components.interfaces.nsIPyIfpmsAlarmRecord);
    Ifpms.Xpcom.DCMgmt.confirmAlarm(id,global_currentuseracc,notes);
    // alarm.confirm_notes=notes;
    // alarm.is_confirmed=true;
    // alarm.confirm_operator=global_currentuseracc;
    // var nti=new Date();
    //alarm.confirm_time精度有限 只能保存到秒数 保存毫秒产生异常
    // alarm.confirm_time=parseInt(nti.getTime()/1000);
	//确认吿警 关闭播放声音
	//jsdump('try to confirm alarm id :'+id);
	for(var i in global_unpro_alarms)
	{
	  if(global_unpro_alarms[i].alarmid==id)
	     {
		   global_unpro_alarms.splice(i,1);
		  // jsdump('confirm alarm id : '+id);
		 }
	}
	for(var j in global_alarmwins)//关闭可能打开的 吿警处理对话框
	{
	   if(typeof(global_alarmwins[j].alarm)=='undefined'){ continue;}
	   if(global_alarmwins[j].alarm.alarmid==id)
	   {
	    global_alarmwins[j].close();
	    global_alarmwins.splice(j,1);
	   }
	}
	//global_unpro_alarms
},
'redrawTable':function()
{
  //var psize=this.pagesize;  
  //var keyword=document.getElementById('alarm_sortkeyword').value;
  // var method=document.getElementById('alarm_sortmethod').value;
  //this.pagesize=psize;
  this.listlength=Ifpms.Xpcom.DCMgmt.alarm_history.length;
  this.pages=Math.ceil(this.listlength/this.pagesize);
  // if(!this.pages){
  //   return;
  // }else{
      $('#alarm_all_pages').empty();
      for(var i=0;i<this.pages;i++)
      {
        var ite=document.createElement('menuitem');
        ite.setAttribute('label',i+1);
        ite.setAttribute('value',i+1);
        document.getElementById('alarm_all_pages').appendChild(ite);
      }
  // }
  if(this.currentpage>this.pages){this.currentpage=this.pages};
  document.getElementById('alarm_desc_page').value=this.currentpage;  
 // this.currentpage=1;
  //alarmmgmt.sortList(keyword,this.list,method);
  if(this.listlength == 0){
    this.alarm_start = 0;
    this.alarm_end = 0;
  }else if(this.listlength < 20){
    this.alarm_start = 0;
    this.alarm_end=Ifpms.Xpcom.DCMgmt.alarm_history.length;
  }else{
    this.alarm_start = this.listlength-20;
    this.alarm_end=Ifpms.Xpcom.DCMgmt.alarm_history.length;
  }
  jsdump("ini: "+this.alarm_start+","+this.alarm_end);
  this.showCurrentPage();
},
'goToPage':function(page)
{
    this.currentpage=page;
    var page_start = 20;
    var page_end = 0;
    var page_limits = [];
    for(var i=0;i<this.pages;i++){
      page_limits.push((this.listlength-page_start)+","+(this.listlength-page_end));
      page_start+=20;
      page_end+=20;
    }
    var page_limit = page_limits[page-1];
    var m_index = page_limit.indexOf(",");
    this.alarm_start = page_limit.substring(0,m_index);
    this.alarm_end = page_limit.substring(m_index+1,page_limit.length);
    this.alarm_start = this.alarm_start<0?0:this.alarm_start;
    jsdump("gotopage: "+this.alarm_start+"-"+this.alarm_end);
    this.showCurrentPage();
}
};

$("#alarm_table_body :button").live("click",function(){
    var alarmInfo = new Array();
    alarmInfo[0]=$(this).get(0).getAttribute("aid");
    alarmInfo[1]=$(this).get(0).getAttribute("did");
    alarmInfo[2]=$(this).get(0).getAttribute("pid");
    alarmInfo[3]=$(this).get(0).getAttribute("time");
    alarmInfo[4]=$(this).get(0).getAttribute("confirmstr");
    alarmInfo[5]=$(this).get(0).getAttribute("note");
    alarmInfo[6]=$(this).get(0).getAttribute("alarmsId");
    alarmmgmt.tablemanager.showAudio(alarmInfo);
})

function convertBinToDecimal(bin)
{
 var de=0;
 var radix=1;
 while(bin!=0)
 {
    de+=(bin%10)*radix;
    radix=radix*2;
    bin=parseInt(bin/10);
 }
 return de;
}

function convertDecimalToBin(dec)
{
    var bin=0;
    var radix=1;
    while(dec!=0)
    {
        bin+=(dec%2)*radix;
        radix=radix*10;
        dec=parseInt(dec/2);
    }
    return bin;
}

alarmmgmt.sortList=function(key,list,method)
{
if(method=='0')
{
 list.sort(alarmmgmt.compareEle[key]);
}
else{
   list.sort(alarmmgmt.compareEle[key]);
   list.reverse();
}
}
alarmmgmt.compareEle={
    'id':function(a,b){
        
        return a.id-b.id;
    },
    'aid':function(a,b)
    {
        return a.aid-b.aid;
    },
    'pid':function(a,b)
    {
        return a.pid-b.pid;
    },
    'did':function(a,b)
    {
        return a.did-b.did;
    },
    'happen_time':function(a,b)
    {
        return a.happen_time-b.happen_time;
    },
    'confirm_time':function(a,b)
    {
        return a.confirm_time-b.confirm_time;
    },
    'is_confirmed':function(a,b)
    {
        return a.is_confirmed-b.is_confirmed;
    },
    'confirm_operator':function(a,b)
    {
       // return ;
    }
    
}
alarmmgmt.getIndexByID=function(id)
{
    for(var i=0;i<Ifpms.Xpcom.DCMgmt.alarm_history.length;i++)
    {
      var alarm=Ifpms.Xpcom.DCMgmt.alarm_history.queryElementAt(i,Components.interfaces.nsIPyIfpmsAlarmRecord);
      if(alarm.id==id) return i;
    }
return -1;
}
alarmmgmt.makeTD=function(text)
{
    var td=document.createElementNS("http://www.w3.org/1999/xhtml","html:td");
    var textcell=document.createElement('label');
    textcell.setAttribute('value',text);
    td.appendChild(textcell);
    td.setAttribute('align','center');
    return td; 
}

function alarmObserver ()
{
   this.register();
}
alarmObserver.prototype={
      observe: function(subject, topic, data) {//产生新的告警
     // Do your stuff here.
     var ar=data.split('-');
     if(ar[2]<4){
        return;
     }
     var strbun=document.getElementById('alarm_str');
     var str=strbun.getFormattedString('newalarm',[ar[0]+"-"+ar[1],alarmmgmt.typeinfo[ar[2]]]);
     document.getElementById('alarm_table_title').setAttribute('value',str);
     //mgmt.ini();

     var alarmObj = {aid:ar[2],did:ar[0],pid:ar[1],happen_time:ar[3]};
     var paname = Ifpms.Xpcom.DCMgmt.getDC(alarmObj.did).getPA(alarmObj.pid).name;
     if(alarmObj.aid != 10 && paname != "环境自适应探测器"){
        alarmmgmt.tablemanager.newestAlarm.unshift(alarmObj);
        if(alarmmgmt.tablemanager.newestAlarm.length>5){
          alarmmgmt.tablemanager.newestAlarm.pop();
        }
        alarmmgmt.tablemanager.newestAlarmInit(5);
     }

  	 if (ar[2]==5||ar[2]==7||ar[2]==8)//断纤  开盖  恢复  不用弹出对话框
  	 {
  	    return;
  	 }
     var pa={};
     pa.did=ar[0];
     pa.pid=ar[1];
     pa.aid=ar[2];
     pa.time=parseInt(ar[3]);
  	 pa.alarmid=ar[4];
  	 var flag=true;
  	 for(var i in global_unpro_alarms)
  	 {
  	   var foo=global_unpro_alarms[i];
  	   if (pa.alarmid==foo.alarmid){
        flag=false;
        return;
       }
  	 }
           
  	 if(flag){
      if(paname != "环境自适应探测器"){
        global_unpro_alarms.push(pa);
      }
         if(Ifpms.timer==0){
           global_CheckSound();
           Ifpms.timer=window.setInterval("global_CheckSound();",alarmSoundtime);
         }
  	 }
      // var pafy=Ifpms.Xpcom.DCMgmt.getDC(pa.did).getPA(pa.pid);
      // if(pafy.work_mode!=2){
        if(parseInt(global_alarmproc_mode)==1 && paname != "环境自适应探测器"){
          Global_openAlarmWindow();
        }
      // }
    },
    register:function()
    {
     var observerService = Components.classes["@mozilla.org/observer-service;1"]  
                          .getService(Components.interfaces.nsIObserverService);  
     observerService.addObserver(this, "eventNewAlarm", false); 
    },
    unregister: function() {
    var observerService = Components.classes["@mozilla.org/observer-service;1"]  
                            .getService(Components.interfaces.nsIObserverService);  
    observerService.removeObserver(this, "eventNewAlarm");
  }
}
alarmmgmt.observer=new alarmObserver();
function  alarmobservernotify(did,pid,aid,time,alarmid)
{
      var observerService_alarm = Components.classes["@mozilla.org/observer-service;1"].  
      getService(Components.interfaces.nsIObserverService);
      var subject = Components.classes["@mozilla.org/supports-string;1"].  
      createInstance(Components.interfaces.nsISupportsString);  
      var data=did+"-"+pid+"-"+aid+'-'+time+'-'+alarmid;
      observerService_alarm.notifyObservers(subject,"eventNewAlarm", data);  
}
function  Global_openAlarmWindow()
{
     if(global_unpro_alarms.length<1){ return ;}
     global_alarmproc_win=window.openDialog('chrome://ifpms/content/Alarm_Process.xul','alarmprocess','chrome,centerscreen',0); 
     global_alarmproc_win.focus();
}