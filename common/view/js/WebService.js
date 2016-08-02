function WebService(sn) {
	this.cache={"foo":2};
	this.c=null;
}

WebService.prototype = {
	send : function(action,request,response_handler,response_handler_params) {
		$.ajax( {
			url : '/json/'+this.c+'/'+action+'/',
			type : 'POST',
			data : request,
			dataType : "json",
			success : function(response) {
				if (typeof response_handler =='function'){
					response_handler(response,response_handler_params);
				}
			},
			error: function(XMLHttpRequest, textStatus, errorThrown){
				if (typeof response_handler =='function'){
					response=JSON.parse(XMLHttpRequest.responseText)
					response_handler(response,response_handler_params);
				}
			},
			complete: function(a,b,c){
				var foo='bar';
			}
		});
	}
}

function AdorechestraWebService() {
	this.c = "home";
}

AdorechestraWebService.prototype = {
	get_random_question:function(response_handler){
		this.send( 'get_random_question',{'null':null},response_handler);
	}
}

AdorechestraWebService.prototype.__proto__ = WebService.prototype;

function UserWebService() {
	this.c = "user";
}
UserWebService.prototype = {
		login : function(username,password,response_handler,response_handler_params) {
			/*
			var host=window.location.host;
			var m=host.match('127.0.0.1');
			protocol='https';
			if(m != null && m.length>0 && m[0]=='127.0.0.1'){
				protocol='http';
			}else{
				var m=host.match('localhost');
				if(m!=null && m.length>0 && m[0]=='localhost'){
					protocol='http';
				}
			}
		
			$.ajax( {
				url : protocol+'://'+window.location.host+'/json/user/login/',
				type : 'POST',
				data : {"username": username,"password":password},
				dataType : "json",
				success : function(response) {
					if (typeof response_handler =='function'){
						response_handler(response,response_handler_params);
					}
				},
				error: function(XMLHttpRequest, textStatus, errorThrown){
					if (typeof response_handler =='function'){
						response_handler({rc:1,rm:'a system error ocurred',model:null});
					}
				},
				complete: function(a,b,c){
					var foo='bar';
				}
			});
			*/
			this.send( 'login',{"username": username,"password":password},response_handler);
		},
		logout : function(response_handler) {
			this.send( 'logout',{"a":"b"},response_handler);
		},
		signup : function(username,password,vpassword,response_handler,response_handler_params) {
		/*
			var host=window.location.host;
			var m=host.match('127.0.0.1');
			protocol='https';
			if(m != null && m.length>0 && m[0]=='127.0.0.1'){
				protocol='http';
			}else{
				var m=host.match('localhost');
				if(m!=null && m.length>0 && m[0]=='localhost'){
					protocol='http';
				}
			}
		
			$.ajax( {
				url : protocol+'://'+window.location.host+'/json/user/signup/',
				type : 'POST',
				data : {"username": username,"password":password,"vpassword":vpassword},
				dataType : "json",
				success : function(response) {
					if (typeof response_handler =='function'){
						response_handler(response,response_handler_params);
					}
				},
				error: function(XMLHttpRequest, textStatus, errorThrown){
					if (typeof response_handler =='function'){
						response_handler({rc:1,rm:'a system error ocurred',model:null});
					}
				},
				complete: function(a,b,c){
					var foo='bar';
				}
			});
			*/
			this.send( 'signup',{"username": username,"password":password,"vpassword":vpassword},response_handler);
		},
		set_email:function(email,response_handler,response_params) {
			this.send('set_email', {"email" : email,"approve":true}, response_handler,response_params);
		}
}
UserWebService.prototype.__proto__ = WebService.prototype;