
function close_message() {
    document.getElementById("message-box").style.display="none";
}

function switch_view(class_name) {
    let listings = document.getElementById("listings");
    listings.className = `gallery-${class_name}`;
    anchor = document.getElementById(class_name);
    active_anchor(anchor);
}

function active_anchor(element){
    let class_name = element.className;
    all = document.getElementsByClassName(class_name);
    for (let i = 0; i < all.length; i++){
        all[i].className = all[i].className.replace(" active", "");
    }
    element.className += " active";
}

//opens and closes single element
function toggle(element_id){
    let menu = document.getElementById(element_id)
    if(menu.style.display === "none"){
        menu.style.display = "grid";
    } else {
        menu.style.display = "none";
    }
}

function reply(element_id){
    let thread = document.getElementById(element_id);
    let reply_form = thread.lastElementChild
    reply_form.style.display="flex";
}
