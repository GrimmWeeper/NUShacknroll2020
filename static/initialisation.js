fetchNotes().then(function(val){
    populateNotes(val);
});
// fetchMessages().then()
populateMessages();
function populateMessages(){
    var json = '{{ pinned_data }}';
    console.log(json);

    for(msg in json){
        console.log(json[msg]);
    }
}


async function fetchNotes(){
    //fetch from firebase the notecollection, and parse document name as its title
    return $.ajax({
        url: '/',
        data:"{{ board }}",
        type: 'POST',
        success: function(response){
            console.log(response);
        },
        error: function(error){
            console.log(error);
        }
    });
   
}

function populateNotes(notecollection){
    const keys = Object.keys(notecollection);

    for(key in keys){  
        var notecontent = notecollection[keys[key]];
        addNewNote(notecontent["title"],notecontent["body"],notecontent["color"],notecontent["height"],notecontent["width"],notecontent["left"],notecontent["top"]);
    }
}

function addnewText(e){
    var content = "content here: emoji here" ; 
    var body1 = document.createElement("body");
    body1.innerHTML = content;
    body1.contentEditable="true";
    body1.classList.add('body');
    var listofbody = this.parentNode.getElementsByClassName('body');
    this.parentNode.insertBefore(body1,listofbody[listofbody.length-1].nextSibling);
    $('.body').draggable();

}
function addNewNote(title="title",body={"enter text here":"emoji"},color="green",height="300px",width="100px",left="500px",top="500px"){
    var notenode = document.createElement('div');                
    notenode.classList.add('note');
    notenode.contentEditable='true';
    var button = document.createElement('button');
    button.style.right = '0px';
    button.style.top = '0px';
    notenode.appendChild(button);
    button.addEventListener('click',addnewText);
    var header = document.createElement("header");
    header.innerHTML = title;
    header.contentEditable = "true";
    header.classList.add('title');
    notenode.appendChild(header);
    const keys = Object.keys(body);
    for(key in keys){
        var content = keys[key] + ": " +body[keys[key]] ; 
        var body1 = document.createElement("body");
        body1.innerHTML = content;
        body1.contentEditable="true";
        body1.classList.add('body');
        notenode.appendChild(body1);
    }    
    notenode.style.backgroundColor = color;
    notenode.style.height=height;
    notenode.style.width=width;
    notenode.style.left=left;
    notenode.style.top=top;

    document.getElementById("noteslist").appendChild(notenode);
    $('.note').draggable();
    $('.note').droppable({
        drop:function(event,ui){
            console.log(this);
            var listofbody = this.getElementsByClassName('body');
                
            this.insertBefore($( ui.draggable )[0],listofbody[listofbody.length-1].nextSibling);
            listofbody= this.getElementsByClassName('body');
            listofbody[listofbody.length-1].style.left = "0px";
            listofbody[listofbody.length-1].style.top = "0px";

            
        }
    });
    $('.body').draggable();
    $('.note').resizable({'aspectRatio' :true});
}
