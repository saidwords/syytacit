var sentencecontroller = null;
$(document).ready( function() {
	sentencecontroller = new Sentencecontroller();
});

function Sentencecontroller() {
	var webservice = new SentenceWebService();
	var data = {
		current_page : 1,
		selected_sentences : [],
		sentences : [],
		question_id : 0,
		questions:[],
		answer_id:0,
		answers: []
	};
	var ui = {
		step_2: $('#step_2'),
		step_3: $('#step_3'),
		step_4: $('#step_4'),
		step_5: $('#step_5'),
		sentences : null,
		tag_selector : $('#tags'),
		sentence_container : $('#sentences'),
		btn_previous : $('#btn_previous'),
		btn_next : $('#btn_next'),
		btn_notasentence : $('button[id^="btn_notasentence-"]'),
		btn_save_question : $('#save_question'),
		btn_delete_question : $('#delete_question'),
		btn_delete_answer:$('img[id^="delete-answer-"]'),
		text_area_question : $('#question'),
		existing_questions: $('#existing_questions'),
		questions: $('span[id^="question-"]'),
		btn_clear_question: $('#btn_clear_question'),
		question_panel:$('#question_panel'),
		btn_save_answer : $('#save_answer'),
		btn_reset_answer : $('#reset_answer'),
		checkbox_iscorrect:$('#iscorrect'),
		answer:$('#answer'),
		div_answers:$('#answers'),
		answers:$('span[id^="answer-"]'),
		selected_sentences : null,
		span_selected_sentence : null,
		show_message: function(response){
			alert(response.rm);
			return true;
		},
		init : function() {
			ui.init_sentences();
			ui.init_selected_sentences();
			ui.tag_selector.change( function() {
				data.current_page=1;
				data.selected_sentences=[];
				ui.selected_sentences.html('');
				ui.existing_questions.html('');
				ui.text_area_question.val('');
				ui.div_answers.html('');
				ui.step_4.hide();
				webservice.getsentences(data.current_page, $(this).val(),handle_get_sentences);
			});
			ui.btn_next.click(ui.next_page);
			ui.btn_previous.click(ui.previous_page);
			ui.btn_save_question.click( function() {
				save_question();
			});
			ui.btn_delete_question.click( function() {
				delete_question();
			});
			ui.btn_clear_question.click(function(){
				data.question_id=0;
				ui.text_area_question.val('');
			});
			
			ui.btn_save_answer.click( function() {
				save_answer();
			});
			ui.btn_reset_answer.click( function() {
				data.answer_id=0;
				ui.answer.val('');
			});
		},
		init_sentences : function() {
			ui.sentences = $('span[id^="sentence-"]');
			ui.sentences.click(ui.select_sentence);
			ui.btn_reject_sentence = $('img[id^="reject-sentence-"]');
			ui.btn_reject_sentence.click(reject_sentence);
			ui.sentences.mouseenter( function() {
				$(this).css('background-color', '#ffff00');
			}).mouseleave( function() {
				$(this).css('background-color', '#ffffff');
			});
		},
		init_selected_sentences : function() {
			ui.selected_sentences = $('#selected_sentences');
			ui.span_selected_sentence = $('span[id^="selected_sentence-"]');
			ui.span_selected_sentence.mouseenter( function() {
				$(this).css('background-color', '#ffff00');
			}).mouseleave( function() {
				$(this).css('background-color', '#ffffff');
			});

			ui.span_selected_sentence.click( function() {
				signature = $(this).attr('id').substr(18);
				remove_sentence(signature);
			});

		},
		init_questions : function() {
			html = '';
			for ( var id in data.questions){
				html += "<span id='question-"
					+ data.questions[id].id + "'>"
					+ data.questions[id].question + "</span><br>";
			}
			
			ui.existing_questions.html(html);
			ui.questions = $('span[id^="question-"]');
			ui.questions.click(ui.select_question);
			ui.questions.mouseenter( function() {
				$(this).css('background-color', '#ffff00');
			}).mouseleave( function() {
				$(this).css('background-color', '#ffffff');
			});
		},
		init_answers:function(){
			html='';
			var foo = data.answers;
			for(i=0;i<data.answers.length;i++){
				html+='<img id="delete-answer-'+data.answers[i].id+'" src="/img/delete.png">'
				+'<span id="answer-'+data.answers[i].id+'">'
				+data.answers[i].answer+'</span><br>';
			}
			ui.div_answers.html(html);

			ui.btn_delete_answer = $('img[id^="delete-answer-"]');
			ui.btn_delete_answer.click(delete_answer);
			ui.answers=$('span[id^="answer-"]');
			ui.answers.click(ui.select_answer);
			
			if(data.answers.length==0){
				ui.checkbox_iscorrect.attr('checked',true);
			}
			
		},
		select_question:function(){
			id=$(this).attr('id').substr(9);
			q=data.questions[id];
			data.question_id=q.id;
			ui.text_area_question.val(q.question);
			data.answers=[];
			ui.step_4.show();
			ui.init_answers();
			webservice.getanswers(data.question_id,handle_get_answers);
		},
		next_page : function() {
			data.current_page++;
			webservice.getsentences(data.current_page, ui.tag_selector.val(),
					handle_get_sentences);
		},
		previous_page : function() {
			data.current_page--;
			if (data.current_page < 2) {
				data.current_page = 1;
			}
			
			webservice.getsentences(data.current_page, ui.tag_selector.val(),handle_get_sentences);
		},
		select_sentence : function() {
			data.question_id=0;
			ui.text_area_question.val('');
			signature = $(this).attr('id').substr(9);

			for (i = 0; i < data.selected_sentences.length; i++) {
				if (data.selected_sentences[i] == signature) {
					return;
				}
			}
			
			
			data.selected_sentences.push(signature);
			ui.update_selected_sentences();
			ui.text_area_question.html('');
			ui.step_3.show();
			data.answers=[];
			data.answer_id=0;
			ui.init_answers();
			webservice.getquestions(data.selected_sentences ,handle_get_questions);
		},
		update_selected_sentences : function() {
			var foo = data.selected_sentences;
			html = '';
			for (i = 0; i < data.selected_sentences.length; i++) {
				signature = data.selected_sentences[i];
				html += '<span id="selected_sentence-' + signature + '">';
				html += data.sentences[signature].sentence + '</span><br>';
			}
			if(html!=''){
				ui.question_panel.show();
			}else{
				ui.question_panel.hide();
			}
			ui.selected_sentences.html(html);
			ui.init_selected_sentences();
			ui.init_questions();
		},
		select_answer:function(){
			data.answer_id=$(this).attr('id').substr(7);
			
			var answer=false;
			for(var i=0;i<data.answers.length;i++){
				if(data.answers[i].id==data.answer_id){
					answer=data.answers[i]
					break;
				}
			}
			if(answer!=false){
				ui.answer.val(answer.answer);
				ui.checkbox_iscorrect.attr('checked',answer.iscorrect);
			}
		},
		
	};

	ui.init();
	var remove_sentence = function(signature) {
		remove_questions();
		for ( var j = 0; j < data.selected_sentences.length; j++) {
			if (signature == data.selected_sentences[j]) {
				data.selected_sentences.splice(j, 1);
			}
		}
		ui.update_selected_sentences();
	};
	
	var remove_questions=function(){
		var foo = data.questions;
		var bar=data.selected_sentences;
		data.questions=[];
		data.question_id=0;
		
		ui.init_questions();
		// remove all answers
		remove_answers();
	};
	
	var remove_answers=function(){
		data.answers=[];
		data.answer_id=0;
		ui.text_area_question.val('');
		ui.answer.val('');
		ui.init_answers();
	}

	var save_question = function() {
		if(data.selected_sentences.length<1){
			alert('Please select one or more sentences');
			return;
		}
		if(ui.text_area_question.val()==''){
			alert('Please enter a question');
			return;
		}
		webservice.savequestion(data.question_id, ui.text_area_question.val(),data.selected_sentences,ui.tag_selector.val(), handle_save_question);
	};

	var handle_save_question = function(response) {
		if (response.rc != 0) {
			alert(response.rm);
			return;
		}
		data.question_id = response.model.question_id;
		ui.step_4.show();

		ui.btn_save_question.callout( {
			position : "top",
			msg : "Your question has been saved."
		}).mouseleave( function() {
			$(this).callout("destroy");
		});		
	};
	
	var reject_sentence = function() {
		signature = $(this).attr('id').substr(16);
		
		$(this).hide();
		$('#sentence-'+signature).hide();
		
		webservice.rejectsentence(signature ,handle_reject_sentence);
	};
	var handle_reject_sentence = function(response) {
		if (response.rc != 0) {
			alert(response.rm);
			return;
		}
		
	};

	var delete_question = function() {
		if(data.question_id==0 ){
			alert('Please select a question');
			return;
		}
		webservice.deletequestion(data.question_id,handle_delete_question);
	};

	var handle_delete_question = function(response) {
		if (response.rc != 0) {
			alert(response.rm);
			return;
		}
		data.question_id = 0;
		ui.text_area_question.html('');
		remove_questions();
		ui.btn_delete_question.callout( {
			position : "top",
			msg : "Your question has been deleted."
		}).mouseleave( function() {
			$(this).callout("destroy");
		});
	};

	var handle_get_sentences = function(response) {
		//remove all sentences from data.sentences that are not in data.selected_sentences
		for ( var signature in data.sentences) {
			var flag = true;
			for ( var j = 0; j < data.selected_sentences.length; j++) {
				if (signature == data.selected_sentences[j]) {
					flag = false;
				}
			}
			if (flag) {
				delete data.sentences[signature];
			}
		}
		html = '';
		for (i = 0; i < response.model.sentences.length; i++) {
			data.sentences[response.model.sentences[i].signature] = response.model.sentences[i];
			html += "<img id='reject-sentence-"+response.model.sentences[i].signature+"' src='/img/delete.png'>"+
					"<span id='sentence-"+response.model.sentences[i].signature + "'>"
					+ '('+response.model.sentences[i].numquestions+') '+response.model.sentences[i].sentence + "</span><br>";
		}
		ui.sentence_container.html(html);
	    ui.step_2.show();
		ui.init_sentences();
	};
	
	var handle_get_questions = function(response) {
		if(response.rc!=0){
			return ui.show_message(response)
		}
		data.questions=[];
		for (i = 0; i < response.model.questions.length; i++) {
			if(typeof data.questions[response.model.questions[i].id] =="undefined" ){
				data.questions[response.model.questions[i].id] = response.model.questions[i];
			}
		}
		for (var i in data.selected_sentences){
			data.selected_sentences[i].questions=response.model.questions;
		}
		ui.init_questions();
	};
	
	var handle_get_answers = function(response) {
		if(response.rc!=0){
			return ui.show_message(response)
		}
		data.answers=response.model.answers;
		ui.init_answers();
	};
	
	
	var save_answer = function() {
		if(data.question_id==0){
			alert('Please create or select a question');
			return;
		}
		if(ui.answer.val().length<2){
			alert('Please enter an answer');
			return;			
		}
		iscorrect=(ui.checkbox_iscorrect.attr('checked')=='checked');
		webservice.saveanswer(data.question_id, data.answer_id,ui.answer.val(),iscorrect, handle_save_answer);
	};

	var handle_save_answer = function(response) {
		if (response.rc != 0) {
			alert(response.rm);
			return;
		}
		var foo = data.answers;
		data.answer_id = 0;
		var found=false;
		for(var i=0;i<data.answers.length;i++){
			if(data.answers[i].id==response.model.answer_id){
				data.answers[i]=response.model.answer;
				data.answers[i].id=response.model.answer_id;
				found=true;
				break;
			}
		}
		
		if(!found){
			//var answer={id:response.model.answer_id,answer:response.model.answer}
			response.model.answer.id=response.model.answer_id;
			data.answers.push(response.model.answer);
		}
		
		ui.btn_save_answer.callout( {
			position : "right",
			msg : "Your answer has been saved."
		}).mouseleave( function() {
			$(this).callout("destroy");
		});
		ui.answer.val('');
		ui.checkbox_iscorrect.attr('checked',false);
		ui.init_answers();
	};

	var delete_answer = function() {
		data.answer_id=0;
		id=$(this).attr('id').substr(14);
		for(i=0;i<data.answers.length;i++){
			if(data.answers[i].id==id){
				data.answers.splice(i, 1);
			}
		}
		webservice.deleteanswer(id,handle_delete_answer);
	};

	var handle_delete_answer = function(response) {
		if (response.rc != 0) {
			alert(response.rm);
			return;
		}
		
		ui.init_answers();
	};


}
function SentenceWebService() {
	this.c = "sentence";
};
SentenceWebService.prototype = {
	getsentences : function(page, tag, response_handler) {
		this.send('getsentences', {
			"page" : page,
			"tag" : tag
		}, response_handler);
	},
	rejectsentence : function( signature, response_handler) {
		this.send('rejectsentence', {
			"signature" : signature
		}, response_handler);
	},
	getquestions : function( sentences, response_handler) {
		this.send('getquestions', {
			"sentences" : sentences
		}, response_handler);
	},
	getanswers : function( question_id, response_handler) {
		this.send('getanswers', {
			"question_id" : question_id
		}, response_handler);
	},
	savequestion : function(id, question, sentences, tag,response_handler) {
		this.send('savequestion', {
			"id" : id,
			"question" : question,
			"sentences" : sentences,
			"tag": tag
		}, response_handler);
	},
	deletequestion : function(id,response_handler) {
		this.send('deletequestion', {
			"id" : id
		}, response_handler);
	},
	deleteanswer : function(id,response_handler) {
		this.send('deleteanswer', {
			"id" : id
		}, response_handler);
	},
	saveanswer : function(question_id, answer_id,answer,iscorrect,response_handler) {
		this.send('saveanswer', {
			"question_id" : question_id,
			"answer_id" : answer_id,
			"answer" : answer,
			"is_correct": iscorrect
		}, response_handler);
	}
};
SentenceWebService.prototype.__proto__ = WebService.prototype;