/**
* Project Name:Fire JavaScript Performance Test
* Description：Using Firebug's Console to do the Javascript performance test,help you find performance bottlenecks.
* Author： kacakong@gmail.com  
* Version: v1.0 beta
* Sample: jspt.test(function(){  testFun();  }); 
*/
 var jspt={
	 run:true,
	 limit:20,
	 test:function(callback,name){
	     if (this.run==true){		    
		    if (typeof(console)!="undefined"){
			     var body=callback.toString();		
				 if (name==null){
					var name1= body.replace("function () {\n","");
					var name2= name1.replace("\n}","");
					name=name2;
				 }	 
				 var t1=(new Date()).getTime();
				 callback();				
				 var t2=(new Date()).getTime();	 	 
				 var space=(t2-t1);
				 if (space<this.limit){
					jsdump(" 执行时间："+space+" ms");
				 }else{
					jsdump(" 执行时间："+space+" ms ,请立即优化！");
				 }
			}else{
				 callback();
			}		     
		 }else{
		     callback();
		 }
		 
	 }	 
  }