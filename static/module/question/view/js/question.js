function QuestionController() {
	var webservice = new QuestionWebService();
	var data = {
		user: {username:false}
	};
	var ui = {
		answer_fields:$('.answer-field'),
		true_false_radio:$('.true_false_radio'),
		next_question:$('.next_question'),
		init : function() {
			
			ui.true_false_radio.each(function(index){
				$(this).click(controller.set_tf_answer);
			});
			
			ui.answer_fields.each(function( index ) {
				$(this).keyup(controller.set_answer);
				$(this).focus(ui.reset_answer_indicator);
			});
			ui.next_question.click(controller.get_next_question);
		},
		reset_answer_indicator: function(e) {
			;//var ai=$('#answer_indicator_'+$(this).data('id'));
			;//ia.html("");
		}
		
	};

	var controller = {
		
		init : function() {
			ui.init();
			$(document).bind('LOGGEDIN', function(e,user) {	
				data.user.username=user.username;
				
			});
			$(document).bind('LOGGEDOUT', function(e,userObj) {	
				data.user.username=false;
			});
		},
		set_tf_answer:function(){
		
			if(data.user.username==false){
				$(this).callout(
					{position:"bottom",msg:"You must be logged in"}
				).mouseenter(function() { 
					$(this).callout("destroy"); 
				});
				
				return;
			}
			question=$(this).closest('.article_question');
			var answers=[]
			question.find('.true_false_radio').each(function(index){
				if($(this).attr('checked')=='checked'){
					answers.push($(this).val());
				}
			});
			$(this).data('id',question.data('id'));
			
			if($(this).val().length > 1){
				var ai=question.find(".answer_indicator");
				ai.html("&nbsp;&nbsp;&nbsp;&nbsp;");
				ai.addClass("ajaxcircle");
				
				webservice.set_answer(question.data('id'), answers,question.data('signature'),callbacks.set_answer,$(this));
			}
			
		},
		set_answer : function(e) {
		    if(e.keyCode==13){
				if(data.user.username==false){
					$(this).callout(
						{position:"bottom",msg:"You must be logged in"}
					).mouseleave(function() { 
						$(this).callout("destroy"); 
					});
					
					setTimeout(function(){$(this).callout("destroy");},3000);
					
					return;
				}
				
				question=$(this).closest('.article_question');
				var answers=[]
				question.find('.answer-field').each(function(index){
					answers.push($(this).val());
				});
				$(this).data('id',question.data('id'));
				
				if($(this).val().length > 1){
					var ai=question.find(".answer_indicator");
					ai.html("&nbsp;&nbsp;&nbsp;&nbsp;");
					ai.addClass("ajaxcircle");
					
					webservice.set_answer(question.data('id'), answers,question.data('signature'),callbacks.set_answer,$(this));
				}
			}
		},
		get_next_question:function(e){
		
			if(data.user.username==false){
				$(this).callout(
					{position:"bottom",msg:"You must be logged in"}
				).mouseleave(function() { 
					$(this).callout("destroy"); 
				});
				return false;
			}
			
			var question=$(this).closest('.article_question');
			var ai=question.find(".answer_indicator");
			ai.html("&nbsp;&nbsp;&nbsp;&nbsp;");
			ai.addClass("ajaxcircle");
			webservice.get_next_question(question.data('id'),true,callbacks.get_next_question,question);
		}
	};

	var callbacks = {
		get_next_question : function(response,question) {
			
			var ai=question.find(".answer_indicator");
			ai.html(" ");
			ai.removeClass("ajaxcircle");
			
			if(response==null){
				// this means something bad happened
				return;
			}
			
			if (response.question==null){
				// this means no relevant question was found
				return;
			}
			
			//ui.question.html(response.question.question);
			//ui.question.id=response.question.id;
			// render the question text and set the new question id
			var article_question_div=question.find('.article_question_text');
			var html='';
			if(response.question_type==1){
				for(var i=0;i<response.question.length;i++){
					if(response.question[i]==null){
						html=html+"<input type='text' class='answer-field'>";
					}else{
						html=html+response.question[i];
					}
						
				}
				article_question_div.html(html);
				// rebind all answer_fields
				ui.answer_fields.off();
				ui.answer_fields=$('.answer-field');
				ui.answer_fields.each(function( index ) {
					$(this).keyup(controller.set_answer);
					$(this).focus(ui.reset_answer_indicator);
				});
			
			}else if(response.question_type==2){
				html=html+response.question[0];
				html+="True<input type='radio' class='true_false_radio' name='true_false_radio' value='true'>False<input type='radio' class='true_false_radio' name='true_false_radio' value='false'>";
				article_question_div.html(html);
				
				ui.true_false_radio=$('.true_false_radio');
				ui.true_false_radio.each(function(index){
					$(this).click(controller.set_tf_answer);
				});
			}
			
			
			question.data('id',response.id)
			question.data('signature',response.signature)
			
		},
		set_answer : function(response,callback_params) {
			
			if(response.exception!=null){
				callback_params.callout(
						{position:"bottom",msg:response.exception.message}
				).mouseenter(function() { 
					callback_params.callout("destroy"); 
				});
				return;
			}
			
			
			//tell the user if they answered the question correctly
			var ai=question.find(".answer_indicator");
			ai.removeClass("ajaxcircle");
			
			if(response.iscorrect==true){
				ai.html("correct");
				ai.css("color","rgba(8,165, 8, 0.91)");
			}else if(response.iscorrect==false){
				ai.html("wrong");
				ai.css("color","rgba(165, 8, 8, 0.91)");
			}else{
				ai.html("");
			} 
			
		}

	};

	var init = function() {
		controller.init();
	};

	return {
		data : data,
		init : init
	};

};
