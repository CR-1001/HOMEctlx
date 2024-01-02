/* This file is part of HomeCtl. Copyright (C) 2023 Christian Rauch.
   Distributed under terms of the GPL3 license. */
   
$(document).ready(function() {

    // load the state table
    load_states(get_type())

    // react to changed attributes: hue, sat, bri
    $(document).on("input", function(event) {

        val  = $(event.target).val()
        attr = get_data(event.target, "attr")
        id   = get_data(event.target, "id")
        type = get_data(event.target, "type")

        set_state(attr, val, id, type)
    })

    // react to changed attributes: pwr
    $(document).on("click", ".txt-pwr", function (event) {

        val  = $(this).html().trim() == "[turn on]" ? "on" : "off"
        id   = get_data(this, "id")
        type = get_data(this, "type")

        set_state("pwr", val, id, type)
    })

    // react to click on a device, set control visible
    $(document).on("click", "[data-id]", function (event) {
        
        id   = get_data(this, "id")
        type = get_data(this, "type")

        set_search_parameter("active", `${type}-${id}`)
        
        // set visibility
        set_visible(`.control`, false)
        set_visible(`[data-id='${id}'][data-type='${type}'] .control`, true)
    })
})


// set state
function set_state(attr, val, id, type) {

    data = { 
        attr: attr, 
        val: val 
    }

    // debounce user input
    clearTimeout(document.state_change_call)
    document.state_change_call = setTimeout(_ => {

        // set the attributes
        fetch(`set-${type}/${id}` , { 
            method: "POST", 
            body: JSON.stringify(data) 
        })
        .then(data => {

            load_states(get_type())
        })

    }, 500)
}


// load the states (prerendered HTML)
function load_states(type) {

    active = get_search_parameter("active", -1)

    fetch(`states-${type}?active=${active}`)
        .then(response => response.text())
        .then(html => {

            $("#states").html(html)
        })
}


// get type: dev or grp
function get_type() {
    return get_data("#states", "type")
}