function QuestionBrowser() {
	var webservice = new QuestionWebService();
	var data = {
		tags : [],
		question : {}
	};
	var ui = {
		answer_fields:$('.answer_field'),
		new_question:$('.new_question'),
		new_answer:$('.new_answer'),
		new_question_tags:$('#new_question_tags'),
		btn_save_new_question:$('#btn_save_new_question'),
		btn_create_question:$('.btn_save_question'),
		question_textarea:$('.question_textarea'),
		question_status:$('.question_status'),
		delete_tag:$('.delete_tag'),
		add_tag:$('.add_tag'),
		delete_question:$('.delete_question'),
		correct_answer:$('.correct_answer'),
		message:$('#message'),
		question_not_possible:$('.question_not_possible'),
		tf_answer:$('.tf_answer'),
		fib_answers:$('#fib_answers'),
		init : function() {
			ui.answer_fields.blur(ui.add_new_answer_field);
			ui.btn_save_new_question.click(controller.new_question);
			ui.btn_create_question.click(controller.create_question);
			ui.question_textarea.change(controller.update_question);
			ui.question_status.change(controller.update_question_status);
			ui.correct_answer.change(controller.update_answer);
			ui.delete_question.click(controller.delete_question);
			ui.tf_answer.change(controller.create_question);
			ui.delete_tag.click(controller.delete_tag);
			ui.add_tag.click(controller.add_tag);
			ui.new_question.change(controller.deduce_answer);
			ui.question_not_possible.click(controller.question_not_possible);
			/*
			ui.question_type.change(function(){
				var sentence=$(this).closest('.sentence');
				var fib_answers=sentence.find('.fib_answers');
				var tf_answers=sentence.find('.tf_answers');
				
				if($(this).val()=='fib'){
					fib_answers.show();
					tf_answers.hide();
				}else{
					fib_answers.hide();
					tf_answers.show();
				}
			});
			*/
		},
		showmessage:function(response,message){
			if(response.exception!=null){
				message=response.exception.message;	
			}
			
			ui.message.callout(
				{position:"top",msg:message}
			).mouseleave(function() { 
				$(this).callout("destroy"); 
			});
		
		},
		add_new_answer_field:function(){
			var fib_answers = $(this).closest('.fib_answers');
			var answer_fields=fib_answers.find('.answer_field');
			
			var addfield=false;
			answer_fields.each(function(index){
				if($(this).val().length>0){
					addfield=true;
				}
			});
			if(addfield){
				var answer_field=$('<input class="answer_field" type="text" placeholder="answer">');
				answer_field.blur(ui.add_new_answer_field);
				answer_field.appendTo(fib_answers);
				
			}
		}
		
	};

	var controller = {
		
		init : function() {
			;
		},
		
		set_answer:function(){
			;
		},
		detach_answer:function(){
			;
		},
		deduce_answer:function(){
		// TODO: compare the changed question text to the new question. 
		// if a word has been replaced with a blank then put the word into the answer_field
		},
		question_not_possible:function(){
			var sentence=$(this).closest('.sentence');
			var sentence_key=sentence.data('key');
			var status=5; //rejected
			webservice.set_sentence_status(status,sentence_key,ajaxhandlers.question_not_possible,$(this));
			return false;
		},
		create_question:function(){
			tags=[]
			var sentence=$(this).closest('.sentence');
			var sentence_key=sentence.data('key');
			var question=sentence.find('.new_question');
			var answer_text=[]
			var q_type=null;
			
			// if there is any text in the answer_fields then its a "fill in the blank" question
			var answer_field=sentence.find('.answer_field');
			answer_field.each(function(index){
				if($(this).val().length>1){
					q_type='fib';
					answer_text.push($(this).val());
				}
			});
		
			// if there are no answers specified and a true/false has been checked, then its a tf question
			if(answer_text.length==0){
				var tf_answer=sentence.find('.tf_answer');
				var checked=tf_answer.filter(':checked').val();
				if(checked != undefined){
					q_type='tf'
					answer_text.push(checked);
				}
			}
			
			// if there are still no answer selected then tell the user
			if(answer_text.length==0){
				alert("Please provide an answer to the question");
				return false;
			}
			
			if(q_type=='fib'){
				var n = question.val().indexOf("__");
				if(n<0){
					alert("please put a blank in the question text area where the word used to be");
					return false;
				}
			}
			
			//question_text,answer_text,tags,sentence_key
			webservice.create(question.val(),answer_text,tags,sentence_key,q_type,ajaxhandlers.create_question,{element:$(this)});
			return false;
		},
		new_question:function(){
			tags=[]
			var sentence=$(this).closest('.sentence');
			var sentence_key=sentence.data('key');
			//var question=$(this).siblings('.new_question');
			
			webservice.create($(this).val(),null,tags,sentence_key,ajaxhandlers.new_question,{element:$(this)});
		},
		delete_question:function(){
			key=$(this).data('key');
			
			webservice.delete_question(key,ajaxhandlers.delete_question);
		},
		delete_tag:function(){
			key=$(this).data('key');
			tag=$(this).data('tag');
			webservice.delete_category(key,tag,ajaxhandlers.delete_tag);
		},
		update_question:function(){
			key=$(this).data('key');
			
			webservice.update(key,$(this).val(),ajaxhandlers.update_question);
		},
		update_question_status:function(){
			key=$(this).data('key');
			
			webservice.update_status(key,$(this).val(),ajaxhandlers.update_question);
		},
		update_answer:function(){
			key=$(this).data('key');
			
			webservice.update_answer(key,$(this).val(),ajaxhandlers.update_answer);
		},
		add_tag:function(){
			key=$(this).data('key');
			tag=$('#new_tag-'+key);
			webservice.add_category(key,tag.val(),ajaxhandlers.add_tag);
		},
		
	};

	

	var ajaxhandlers = {
		question_not_possible:function(response,params){
		    params.callout(
				{position:"right",msg:"Sentence has been removed from the database"}
			).mouseenter(function() { 
				$(this).callout("destroy"); 
			});
			
		},
		update_question : function(response) {
			ui.showmessage(response,"Question updated");
		},
		update_answer : function(response) {
			ui.showmessage(response,"Answer updated");
		},
		delete_question : function(response) {
			ui.showmessage(response,"Question Deleted");
		},
		delete_tag : function(response) {
			ui.showmessage(response,"Tag deleted from question");
		
		},
		create_question : function(response,params) {
			
			if(response.exception!=null){
				alert(response.exception.message);
				return false;	
			}
			
			params.element.callout(
				{position:"right",msg:"Question created"}
			).mouseenter(function() { 
				$(this).callout("destroy"); 
			});
			
			
		},
		new_question : function(response,params) {
			
			ui.btn_save_new_question.data('key',response.key);
			
			if(response.exception!=null){
				message=response.exception.message;	
			}
			
			params.element.callout(
				{position:"top",msg:"Question created"}
			).mouseleave(function() { 
				$(this).callout("destroy"); 
			});
			
		},
		add_tag:function(response){
			ui.showmessage(response,"Tag added");
			
		}
		
	};

	var init = function() {
		controller.init();
		ui.init();
	};

	return {
		data : data,
		init : init
	};

};
