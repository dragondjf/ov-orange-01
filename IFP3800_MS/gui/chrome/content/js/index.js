mgmt={};
mgmt.ini=function()
{
this.tablemanager.ini();//初始化
}
mgmt.tablemanager={
    'list':[],
    'getAlarmlist':function()//获取告警列表
    {
	this.list.splice(0,this.list.length);//删除list中的所有数据
	for(var i=0;i<Ifpms.Xpcom.DCMgmt.alarm_history.length;i++)
	 {
	     var alarm=Ifpms.Xpcom.DCMgmt.alarm_history.queryElementAt(i,Components.interfaces.nsIPyIfpmsAlarmRecord);//取一条数据
         if(alarm.aid >= 4){
            this.list.push(alarm);//将数据放入list中
         }
	 }
    },
    'showCurrentPage':function(pagesize){
	$("#index_alarm_body").empty();
	pagesize=pagesize<this.list.length?pagesize:this.list.length;
	for(var i=0; i<pagesize; i++){
	   var tr=document.createElementNS("http://www.w3.org/1999/xhtml","html:tr");
	   var alarmid=this.list[i].aid;
	   var alarmtype=alarmmgmt.typeinfo[this.list[i].aid];
	   var td1=alarmmgmt.makeTD(alarmtype);
	   var did=this.list[i].did;
	   var pid=this.list[i].pid;
	   var pa;
	   var name;
	   if(did!=0&&pid!=0){
	      pa=Ifpms.Xpcom.DCMgmt.getDC(did).getPA(pid);
	      name=pa.name;
	   }else{
	      name="---";
	   }	   
	   var td2=alarmmgmt.makeTD(name);
	   var strTime=new Date(parseInt(this.list[i].happen_time)*1000).toLocaleString();
	   var td3=alarmmgmt.makeTD(strTime);
	   tr.appendChild(td1);
	   tr.appendChild(td2);
	   tr.appendChild(td3);
	   $("#index_alarm_body").append(tr);
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
    'ini':function(){
	//alert("aaaaaaa");
	this.getAlarmlist();
	mgmt.sortList(this.list);
	this.showCurrentPage(5);
    }
};

mgmt.sortList=function(list)//排序
{
     list.sort(mgmt.compareEle['happen_time']);
     list.reverse();
}

mgmt.compareEle={
    'happen_time':function(a,b)
    {
        return a.happen_time-b.happen_time;
    }   
}
