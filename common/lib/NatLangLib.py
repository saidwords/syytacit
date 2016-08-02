# coding=UTF-8
# -*- coding: UTF-8 -*-
import logging
class NatLangLib:

    stopwords=['a','able','about','across','after','all','almost','also','am','among','an','and','any','are','as','at','be','because','been','but','by','can','cannot','could','dear','did','do','does','either','else','ever','every','for','from','get','got','had','has','have','he','her','hers','him','his','how','however','i','if','in','into','is','it','its','just','least','let','like','likely','may','me','might','most','must','my','neither','no','nor','not','of','off','often','on','only','or','other','our','own','rather','said','say','says','she','should','since','so','some','than','that','the','their','them','then','there','these','they','this','tis','to','too','twas','us','wants','was','we','were','what','when','where','which','while','who','whom','why','will','with','would','yet','you','your','above','afterwards','again','against','alone','along','already','although','always','amongst','amoungst','amount','another','anyhow','anyone','anything','anyway','anywhere','around','back','became','become','becomes','becoming','before','beforehand','behind','being','below','beside','besides','between','beyond','bill','both','bottom','call','cant','co','con','couldnt','cry','de','describe','detail','done','down','due','during','each','eg','eight','eleven','elsewhere','empty','enough','etc','even','everyone','everything','everywhere','except','few','fifteen','fify','fill','find','fire','first','five','former','formerly','forty','found','four','front','full','further','give','go','hasnt','hence','here','hereafter','hereby','herein','hereupon','herself','himself','hundred','ie','inc','indeed','interest','itself','keep','last','latter','latterly','less','ltd','made','many','meanwhile','mill','mine','more','moreover','mostly','move','much','myself','name','namely','never','nevertheless','next','nine','nobody','none','noone','nothing','now','nowhere','once','one','onto','others','otherwise','ours','ourselves','out','over','part','per','perhaps','please','put','re','same','see','seem','seemed','seeming','seems','serious','several','show','side','sincere','six','sixty','somehow','someone','something','sometime','sometimes','somewhere','still','such','system','take','ten','themselves','thence','thereafter','thereby','therefore','therein','thereupon','thickv','thin','third','those','though','three','through','throughout','thru','thus','together','top','toward','towards','twelve','twenty','two','un','under','until','up','upon','very','via','well','whatever','whence','whenever','whereafter','whereas','whereby','wherein','whereupon','wherever','whether','whither','whoever','whole','whose','within','without','yours','yourself','yourselves','according','accordingly','actually','aint','allow','allows','anybody','anyways','apart','appear','appreciate','appropriate','arent','aside','ask','asking','associated','available','away','awfully','believe','best','better','brief','cmon','cs','came','cause','causes','certain','certainly','changes','clearly','com','come','comes','concerning','consequently','consider','considering','contain','containing','contains','corresponding','course','currently','definitely','described','despite','didnt','different','doesnt','doing','dont','downwards','edu','entirely','especially','et','everybody','ex','exactly','example','far','fifth','followed','following','follows','forth','furthermore','gets','getting','given','gives','goes','going','gone','gotten','greetings','hadnt','happens','hardly','havent','having','hes','hello','help','heres','hi','hither','hopefully','howbeit','id','ill','im','ive','ignored','immediate','inasmuch','indicate','indicated','indicates','inner','insofar','instead','inward','isnt','itd','itll','keeps','kept','know','knows','known','lately','later','lest','lets','liked','little','look','looking','looks','mainly','maybe','mean','merely','nd','near','nearly','necessary','need','needs','new','non','normally','novel','obviously','oh','ok','okay','old','ones','ought','outside','overall','particular','particularly','placed','plus','possible','presumably','probably','provides','que','quite','qv','rd','really','reasonably','regarding','regardless','regards','relatively','respectively','right','saw','saying','second','secondly','seeing','seen','self','selves','sensible','sent','seriously','seven','shall','shouldnt','somebody','somewhat','soon','sorry','specified','specify','specifying','sub','sup','sure','ts','taken','tell','tends','th','thank','thanks','thanx','thats','theirs','theres','theyd','theyll','theyre','theyve','think','thorough','thoroughly','took','tried','tries','truly','try','trying','twice','unfortunately','unless','unlikely','unto','use','used','useful','uses','using','usually','value','various','viz','vs','want','wasnt','way','wed','weve','welcome','went','werent','whats','wheres','whos','willing','wish','wont','wonder','wouldnt','yes','youd','youll','youre','youve','zero']

    def getSentences(paragraph):
        """
        c = lowercase character
        C = uppercase character
        S = whitespace
        N = number
        """
        EOS_marker="_MSC"
        exceptions="cSCMSC"
        sentences=[]
        p="";
        Qstate=0 # qoutes
        Pstate=0 #parenthesis
        Bstate=0 #curly brackets
        i=0
        prev_i=i
        
        for c in paragraph:
            
            if c=="{":
                p=p+"S"
                Bstate=Bstate+1
            elif c=="}":
                p=p+"S"
                Bstate=Bstate-1
                if Bstate<0:
                    logging.error("ERROR: unmatched curly braces")
                    Bstate=0
            
            if Bstate>0:
                p=p+"S"
                    
            elif c==" ":
                p=p+"S"
            elif c=="\n":
                p=p+"S"
            elif c=="?": 
                p=p+"?"
            elif c=="!": 
                p=p+"!"
            elif c==".": 
                p=p+"."
            elif c.isupper():
                p=p+"C"
            elif c.islower():
                p=p+"c"
            elif c.isdigit():
                p=p+"N" 
            
            elif c=="(":
                Pstate=Pstate+1
            elif c==")":
                Pstate=Pstate-1
                if Pstate<0:
                    logging.error("ERROR: unmatched parenthesis")
                    Pstate=0
            elif c=="\"" or c=="'":
                if Qstate==1:
                    Qstate=Qstate+1
                else:
                    Qstate1=Qstate-1
                    if Qstate<0:
                        logging.error( "ERROR: unmatched quotes")
                        Qstate=0
            else:
                p=p+"_"
    
    
            EOS=NatLangLib.matchy(EOS_marker,p)        
    
            if EOS:
                # check for exceptions
                Foo=NatLangLib.matchy(exceptions,p)
                if not Foo:
                    sentences.append((prev_i,i));
                    prev_i=i
    
            i=i+1
        return sentences

    def matchy(EOS_marker,p):
        EOS='False'
        l=len(EOS_marker)
        if l<= len(p):
            pattern=p[-l:]
            j=0;EOS=True
            for x in EOS_marker:
                y=pattern[j]
                if x=="_": # any character
                    pass
                elif x=="S": # whitespace
                    if y=="S":
                        pass
                    else:
                        EOS=False
                elif x=="c": #any lowercase alpha character
                    if y.islower():
                        pass
                    else:
                        EOS=False
                elif x=="C":
                    if y.isupper():
                        pass
                    else:
                        EOS=False
                elif x=="M":
                    if y=="." or y=="!" or y=="?":
                        pass
                    else:
                        EOS=False
                elif x=="N":
                    if y.isdigit():
                        pass
                    else:
                        EOS=False
                elif x==y:
                    pass
                else:
                    EOS=False
                
                j=j+1
        return EOS
    
   
    def num2word(self,number):
        word=number
        
        words=['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
        if number >=0 and number <20:
            word=words[number]
        
        return word
    
    num2word=staticmethod(num2word)
    getSentences=staticmethod(getSentences)
    matchy=staticmethod(matchy)
  