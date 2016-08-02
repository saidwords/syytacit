function Adorechestra(){
	var webservice=new AdorechestraWebService();
	var userwebservice=new UserWebService();
    password=null;
    var ui={
		init:function (){
	        ui.btn_login.click(login);
	        ui.btn_logout.click(logout);
	        ui.btn_signup.click(signup);
	        ui.password.keypress(login);
	        ui.password2.keypress(signup);
		},
		login_message:$('#login_message'),
		password:$('#password'),
		password2:$('#password2'),
		password2_field:$('#password2-field'),
    	btn_signup:$('#btn-signup'),
 	    subtitle:$("#subtitle"),
	    exceptiondiv:$('#exception'),
	    btn_login:$('#btn-login'),
	    btn_logout:$('#btn-logout'),
	    loggedin:$('#loggedin'),
	    loggedout:$('#loggedout'),
	    user:$('#user'),
	    loginfields:$('#login-fields'),
	    username:$('#username')
	    
    };
    
    var controller={
    	init:function(){
    		ui.init();
    	},
    };
    
	var callout_exception=function(element,message){
		//TODO: enable word-wrap
		errormsg=message==null ? 'Sorry, we were unable to process the request. Please try again later':message;
		element.callout(
				{msg:errormsg} 
		).mouseleave(function() { 
			$(this).callout("destroy"); 
		});
	};

	
	var login=function(event){
		
		if(ui.loginfields.css("display")=="none"){
			ui.loginfields.show();
			ui.username.focus();
			return;
		}else{
			if(ui.username.val()==''){
				ui.loginfields.hide();
				ui.login_message.html("");
				return;
			}
		}
		
		if (event.which == 1 || event.which==13){
			if(ui.username.val()=='' && ui.password.val()==''){
	    		ui.loginfields.hide();
	    		return false;
	    	}
	    	if(ui.username.val()==''){
	    		ui.username.callout(
	    			{position:"left",msg:'Enter your username in this box'}
	    		).mouseleave(function() { 
					$(this).callout("destroy"); 
				});
	    		return false;
	    	}
	    	if(ui.password.val()==''){
	    		ui.password.callout(
	    			{position:"left",msg:'Enter your password in this box'}
	    		).mouseleave(function() { 
					$(this).callout("destroy"); 
				});
	    		return false;
	    	}
	    	ui.btn_login.attr("disabled", true);
	    	ui.login_message.html("logging in...");
	    	
	    	userwebservice.login(ui.username.val(),ui.password.val(),handle_login);
		}
	};
	
	var handle_login=function(response){
		ui.btn_login.attr("disabled", false);
		ui.btn_login.html("Login");
			
		if(response.exception==null){
			if(response.user.username){
				mesg="You have been logged in!";
				ui.loginfields.hide();
				ui.btn_login.hide();
				ui.btn_signup.hide();
				ui.btn_logout.show();
				ui.user.html(response.user.username);
				ui.user.attr("href","/user/home/"+response.user.username);
				ui.user.show();
				$(document).trigger('LOGGEDIN',response);
			}else{
				mesg='Sorry. the username or password is not recognized';
			}

		}else if (response.exception.type=='InvalidPasswordError'|| response.exception.type=='InvalidAuthIdError'){
			mesg='Sorry. the username or password is not recognized';
		}else{
			mesg='Sorry. We are unable to let you in right now.';
		}
		
		ui.login_message.html(mesg);
		
		
	};
	var logout=function(){
		ui.btn_logout.attr("disabled", true);
		userwebservice.logout(handle_logout);
	};
	var handle_logout=function(response){
		ui.btn_logout.attr("disabled", false);
		ui.btn_login.show();
		ui.btn_signup.show();
		ui.btn_logout.hide();
		ui.user.hide();
		$(document).trigger('LOGGEDOUT',response.model);
	}
	var signup=function(event){
		
		if(ui.loginfields.css("display")=="none"){
			ui.loginfields.show();
			ui.password2_field.show();
			ui.username.focus();
			return;
		}
		
		if(ui.password2_field.css("display")=="none"){
			ui.password2_field.show();
			return;
		}
		if(ui.username.val()=='' && ui.password.val()=='' && ui.password2.val()==''){
			ui.loginfields.hide();
			ui.login_message.html("");
			ui.password2_field.hide();
			return;
		}
		if (event.which == 1 || event.which==13){
			if(ui.password2.val()==''){
	    		ui.password2.callout(
	    			{position:"left",msg:'Retype your password in this box'}
	    		).mouseleave(function() { 
					$(this).callout("destroy"); 
				});
	    		return false;
	    	}
	    	
	    	if(ui.password.val()==''){
	    		ui.password.callout(
	    			{position:"left",msg:'Enter your password in this box'}
	    		).mouseleave(function() { 
					$(this).callout("destroy"); 
				});
	    		return false;
	    	}
	    	
			if(ui.password.val()!=ui.password2.val()){
				ui.password.callout(
	    			{position:"left",msg:'Oops, I think you may have mis-typed your password.<br>Please try again'}
	    		).mouseleave(function() { 
					$(this).callout("destroy"); 
				});
				return false;
			}
	    	
	    	ui.btn_signup.attr("disabled", true);
	    	ui.login_message.html("registering...");
	    	userwebservice.signup(ui.username.val(),ui.password.val(),ui.password.val(),handle_signup);
	    	return;
    	}
		
	};
	
	var handle_signup=function(response){
		ui.btn_signup.attr("disabled", false);
		if(response.exception==null ){
			handle_login(response);
		}else{
			ui.login_message.html(response.exception.message);
			
		}
	};
	
	return {
		init: controller.init
	};

}