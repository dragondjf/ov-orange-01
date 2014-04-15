var debug={};
debug.dataNames=['freq','max','min','spread','prewarn','data0','data1','data2','data3','data4','data5','data6',
                 'data7','data8','data9'];//数据源名称
debug.plotcolors=['blue','red','green','purple','orange','pink','#fefedd','#feefde','#808080','#88fefe','blue','red','green','purple','orange'];
debug.wave_obj=[{'id':'frequency','y_title':'fre','x_title':'fre_sample','sampletype':[0]},
                    {'id':'maxmin','y_title':'maxmin','x_title':'maxmin_sample','type':'2',
                    'buffn1':'max','buffn2':'min','sampletype':[1,2]},
                    {'id':'spread','y_title':'spread','x_title':'spread_sample','sampletype':[3,1,4]},
                    {'id':'prewarn','y_title':'prewarn','x_title':'prewarn_sample','sampletype':[4]}//,
                    //{'id':'data2','y_title':'prewarn','x_title':'prewarn_sample','sampletype':'data2'}
                     ];
debug.loadMode=false;
function waveType(ar,sid)
{
    this.waveid='';
    this.sid=sid;
    this.rawflag=true;
    this.enableflag=true;
    this.mode=0;//模式0 自动设置y轴范围
    this.framepoints=80;//一帧图形显示多少个点
    this.width=1300;
    this.height=500;
    this.y_caption=50;    
    this.y_cells=16;
    this.ybase=0;
    this.yrange=65535;
    this.y_fa=this.yrange/this.y_cells;    
    this.xbase=0;
    this.xrange=500;
    this.x_cells=64;
    this.timeinfo='null';
    this.x_fa=this.xrange/this.x_cells;
    this.type=1;//1绘制一条线条 2 绘制2条线条
    this.times=[];
    this.showHideTime=0;
    for(var i in ar )
    {
        this[i]=ar[i];
        if(i=='id')
        {
         this.waveid=ar[i];
        }
    }
}
function cls_PA(pid,sid)//防区类  防区id 各种数据
{
    this.pid=pid;
    this.sid=sid;
}
var ShiftWindow=function(idx)//切换窗口
{
//修改样式
$('toolbar toolbarbutton').each(function(){
    $(this).removeClass('tlbarbtnactive');
   });
var childindex=idx+1;
$('toolbar toolbarbutton:nth-child('+childindex+')').addClass('tlbarbtnactive');
    debug.clear_up();//释放资源  
}
debug.changeLayout=function(type)
{
    if(!debug.loaded) {return;}
     var winwid=window.screen.width;//
     var winhei=window.screen.height;
     var cliwid=winwid-60;
     var clihei=winhei-210;
     var defobj={'palist':debug.palist};
     cliwid=cliwid-8;
     var ids=['wave_canvas','sec_wave','third_wave','fourth_wave'];
     for(var i=0;i<ids.length;i++)
     {
	    var nwave=document.getElementById(ids[i]);
	    nwave.setCanvasWidth(cliwid);
	    nwave.hideControl(1);
	    nwave.setId(ids[i]);
	    nwave.initial(defobj,global_wavesetting[i]);
     }
    cliwid+=8;
    if(type==1)// 1*1 
    {
	document.getElementById("wave_canvas").setAttribute("height",clihei);
	document.getElementById("wave_canvas").setAttribute("width",cliwid);
	document.getElementById("wave_canvas").show();
	document.getElementById("sec_wave").hide();
	document.getElementById("sec_wave").style.display='none';//setAttribute("style",'display:none;');
    document.getElementById("third_wave").hide();
	document.getElementById("third_wave").style.display='none';
    document.getElementById("fourth_wave").hide();
	document.getElementById("fourth_wave").style.display='none';
    }
    else if(type==2)
    {
	var hei=clihei/2;
	document.getElementById("wave_canvas").setAttribute("height",hei);
    document.getElementById("wave_canvas").show();
	document.getElementById("sec_wave").style.display='block';
	document.getElementById("sec_wave").setAttribute("height",hei);
	document.getElementById("sec_wave").setAttribute("width",cliwid);
	document.getElementById("sec_wave").show();
    document.getElementById("third_wave").hide();	
	document.getElementById("third_wave").style.display='none';
	document.getElementById("fourth_wave").hide();	
	document.getElementById("fourth_wave").style.display='none';
    }
    else if(type==3){
	var hei=clihei/3;
	document.getElementById("wave_canvas").setAttribute("height",hei);
	document.getElementById("wave_canvas").setAttribute("width",cliwid);
	document.getElementById("sec_wave").style.display='block';
	document.getElementById("sec_wave").setAttribute("height",hei);
	document.getElementById("sec_wave").setAttribute("width",cliwid);
	document.getElementById("third_wave").style.display='block';
	document.getElementById("third_wave").setAttribute("height",hei);
	document.getElementById("third_wave").setAttribute("width",cliwid);
   	document.getElementById("fourth_wave").hide();     
	document.getElementById("fourth_wave").style.display='none';
	document.getElementById("wave_canvas").show();
	document.getElementById("sec_wave").show();	
	document.getElementById("third_wave").show();
    }
    else if(type==4){
	var hei=clihei/4;
	document.getElementById("wave_canvas").setAttribute("height",hei);
	document.getElementById("sec_wave").style.display='block';
	document.getElementById("sec_wave").setAttribute("width",cliwid);
	document.getElementById("sec_wave").setAttribute("height",hei);
	document.getElementById("third_wave").style.display='block';
	document.getElementById("third_wave").setAttribute("height",hei);
	document.getElementById("third_wave").setAttribute("width",cliwid);
	document.getElementById("fourth_wave").style.display='block';
	document.getElementById("fourth_wave").setAttribute("height",hei);
	document.getElementById("fourth_wave").setAttribute("width",cliwid);
	document.getElementById("wave_canvas").show();
	document.getElementById("sec_wave").show();	
	document.getElementById("third_wave").show();
	document.getElementById("fourth_wave").show();	
    }
}
debug.config_debug_info=function()
{   
 //初始化 所有防区对象
    debug.palist=[];
    for(var i=0;i<Ifpms.Xpcom.DCMgmt.pa_list.length; i++)
    {
        var pa = Ifpms.Xpcom.DCMgmt.pa_list.queryElementAt(i,Components.interfaces.nsIPyIfpmsPA);
        var tpa=new cls_PA(i,pa.sid);
	    debug.palist.push(tpa);
    }
}
debug.getWaveByType=function(type)
{
    for(var i=0;i<debug.wave_obj.length;i++)
    {
	if(debug.wave_obj[i].id==type)
	{
	    return debug.wave_obj[i];
	}
    }    
return  debug.wave_obj[0];
}
debug.getSidFromPid=function(pid)
{
    for(var i=0;i<Ifpms.Xpcom.DCMgmt.pa_list.length; i++)
    {
      var pa = Ifpms.Xpcom.DCMgmt.pa_list.queryElementAt(i,Components.interfaces.nsIPyIfpmsPA);
      if(pid==i)
      {
        return pa.sid;
      }
    }
  return 'null';
}
debug.getPidFromSid=function(sid)
{
  for(var i=0;i<Ifpms.Xpcom.DCMgmt.pa_list.length; i++)
  {
      var pa = Ifpms.Xpcom.DCMgmt.pa_list.queryElementAt(i,Components.interfaces.nsIPyIfpmsPA);
      if(sid==pa.sid)
      {
        return i;
      }
  }
  return 'null';
}
debug.changeConfig=function()
{
    if(!debug.palist) {return;}
    var ids=['wave_canvas','sec_wave','third_wave','fourth_wave'];
	var layout=document.getElementById('layoutType').value;
	for(var i=0;i<parseInt(layout);i++)
	{
		 document.getElementById(ids[i]).setWave();
	}
}
debug.initial=function()
{
    var waveState = document.getElementById('pause').getAttribute('state');
    if(waveState == 1){
      return;
    }
    if(!debug.loaded)
    {
        debug.loaded=true;
        this.config_debug_info();// 创建 防区对象
		document.getElementById('layoutType').value=global_wavelayout;
        debug.changeLayout(global_wavelayout);// set layout
    }
    else
	{   // 已经加载过
        debug.config_debug_info();// update pa info 
	    var ids=['wave_canvas','sec_wave','third_wave','fourth_wave'];
	    var layout=document.getElementById('layoutType').value;
	    var defobj={'palist':debug.palist};
	    for(var i=0;i<parseInt(layout);i++)
	    {
		document.getElementById(ids[i]).initial(defobj);
        // alert(ids[i]+' initial.');
	    }
    }
}

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

debug.updateWave=function (pid,wv,offset,points)
{
  var count={};
  var data={};
  var pa = Ifpms.Xpcom.DCMgmt.pa_list.queryElementAt(pid,Components.interfaces.nsIPyIfpmsPA);
  if(pa)
  {
      for(var i=0;i<wv.sampletype.length;i++)
      {
         var sname=debug.dataNames[wv.sampletype[i]];
         var li='plotdata'+i;
         if(typeof(wv[li])=='undefined')
         {
             wv[li]=[];
         }
	 if(typeof(wv["times"])=='undefined'){
	    wv["times"]=[];
	 }
         debug.loadData(pa,sname,offset,points,wv[li],wv["times"]);
      }  
      wv.framepoints=points;  
      wv.xrange=wv.framepoints;
      wv.x_fa=wv.xrange/wv.x_cells;
      debug.applyMode(wv);
  }
  wv.timeinfo=new Date().format("yyyy-MM-dd hh:mm:ss S");
}

debug.loadData=function(pa,sname,offset,points,arr,times) //获取数据放在 数组中    
{
var len=parseInt(offset)+parseInt(points)-1;
    len=len*(-1);
    var count={};
    var data={};
    var time={};
    var off={'value':len};
    pa.getSampling(sname,off,count,data,time);
    times.splice(0,times.length);
    for(var i=0; i<time.value.length; i++){
	times.push(time.value[i]);
    }
    //jsdump("timevalue"+times.join(" "));
    arr.splice(0,arr.length);
    if(count.value>0)
    {
              //jsdump('required data length : '+points+" real length "+data.value.length);
              for (var i=0;i<points;i++)
              {
                 arr.push(data.value[i]); 
              }
    }
    else 
    {
         for(var i=0;i<points;i++)
         {
             arr.push(1); 
         }
    }
}
debug.clear_up=function()//离开时释放资源
{
    document.getElementById("wave_canvas").clearUp();
    document.getElementById("sec_wave").clearUp();	
    document.getElementById("third_wave").clearUp();
    document.getElementById("fourth_wave").clearUp();	
}
debug.applyMode=function(obj)//
{
    if(obj.mode==0)
    {    
     var y_max=0;
     var y_min=1000000;
	for(var i=0;i<obj.sampletype.length;i++)
	{
	 var pl=eval('obj.plotdata'+i);
     if(pl){
	    var re=debug.getMaxMin(y_max,y_min,pl);
             y_max=re.max;
             y_min=re.min;
	 }
	}
    if(y_max==y_min)
    {
        y_max=2*y_min;
        y_min=0;
    }
    if(y_max<y_min)
    {
        y_max=0;
        y_min=0;	 
    }
    obj.ybase=y_min;
    obj.yrange=y_max-y_min;
    obj.y_fa=obj.yrange/obj.y_cells;
    }
    else{
    obj.y_fa=obj.yrange/obj.y_cells;
    }
}

debug.getMaxMin=function(max,min,arr)
{
    var re={};
    re.max=max;
    re.min=min;
    for(var i=0;i<arr.length;i++)
    {
       if(arr[i]>re.max) {re.max=arr[i];}
       if(arr[i]<re.min){re.min=arr[i];}
    }
    return re;
}

debug.modifyfloat=function(num,precision)//按精度去掉小数点后面多余几位 剩余位四舍五入（默认保留两位小数）
{
    var factor=1000;
    if(precision)
    {
        factor=precision;
    }
    var muititho=num*factor;
    var left=muititho%10;
    var oldnum=parseInt(muititho/10);
    if(left==0)//只有两位小数或少于两位小数
    {
      return num;
    }
    var carry=0;
    carry=left+5>=10?1:0;
    factor=factor/10;
    return (oldnum+carry)/factor;
}
debug.fetch_random_data=function(base,range,container)//随机产生 base---base+range范围内的数  放置在container中  
{
   for(i=0;i<10;i++)
   {
    var temp=base+range*Math.random();
    container.push(temp);
   }
    return true;
}
