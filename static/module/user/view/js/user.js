function UserController() {
	var webservice = new UserWebService();
	var data={
		
	};
	var ui={
		btn_change_email:$('#btn_change_email'),
		email:$('#email'),
		
		init:function(){
			ui.btn_change_email.click(controller.change_email);
			
		}
	};
	
	var controller={
		init:function(){
			ui.init();
		},
		change_email:function(){
			
			webservice.set_email(ui.email.val(),ajaxhandlers.change_email);
		}
	};
	
	var ajaxhandlers={
		change_email:function(response,callback_params){
			
			if(response.exception==null){
				
				ui.btn_change_email.callout({position:"right",msg:"Email address has been changed"});
			}else{
				btn_change_email.callout({position:"right",msg:response.exception.message});
				
			}
			setTimeout(function(){callback_params.callout("destroy");},3000);
		}
	};
	
	return {
		init: controller.init,
		data:data
	};
};

