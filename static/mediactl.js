/* This file is part of HomeCtl. Copyright (C) 2023 Christian Rauch.
   Distributed under terms of the GPL3 license. */
   
$(document).ready(function() {
    
    // load directory
    load_dir(get_path(), true, false)

    // react to click on a directory, load it
    $(document).on("click", "[data-dir]", function (event) {
    
        dir = get_data(this, "dir")
        
        load_dir(dir, true, true)
    })

    // load next page
    $(document).on("click", "#btn-next,#btn-prev", function (event) {

        if ($(this).hasClass("inactive")) return

        if ($(this).attr("id") == "btn-next") {
            file_index = get_file_index() + get_page_size()
            push_state_history_with_search_parameter("fileindex", file_index)
        }
        else {
            file_index = get_file_index() - get_page_size()
            if (file_index < 0) file_index = 0
            push_state_history_with_search_parameter("fileindex", file_index)
        }
        
        load_dir(get_path(), false, false)
    })

    // handle pop-state
    $(window).on("popstate", function(event) {

        load_dir(get_path(), false, false)
    })
})


// load directory, reset paging info
function load_dir(dir, with_history, reset_paging) {

    // history
    if (with_history) push_state_history_with_search_parameter("path", dir)

    // paging reset
    if (reset_paging) set_search_parameter("fileindex", 0)

    //$("#paging-header").html("<span class='info'>Loading...</span>")

    // call server
    fetch(`srv-dir/${dir}`)
        .then(response => response.json())
        .then(data => {
            
            document.file_count = 0
            document.dir_count = 0

            set_path(data["path"])
            set_dirs(dir, data["dirs"])
            set_files(dir, data["files"])
            set_pages(data["files"], dir)

            focus_field = get_file_index() > 0 
                ? "files" : "directories"
            $(document).scrollTop($(focus_field))
        })
}


// set path with breadcrumb navigation to parent directories
function set_path(path_parts) {

    path_html = `<span data-dir="$" class="header section-2">ROOT&nbsp;</span>`
    path = ""

    path_parts.forEach(p => {

        if (p == "") return

        path += `/${p}`

        dir = p

        path_html += `<span data-dir="${path}">/&nbsp;${dir}&nbsp;</span>`
    })

    $("#path").html(path_html)
}


// set paging buttons and info
function set_pages(files, dir) {

    begin = get_file_index() + 1
    end   = get_file_index() + get_page_size()
    end   = files.length < end ? files.length : end

    previous_visible = files.length > 0 && begin > 1
    next_visible     = files.length > 0 && files.length > end

    // container begin
    paging_html = `<div class="width-3 flex">`
    
    // file range display
    if (files.length > 0) {

        files_html = `${files.length} files`

        if (files.length != 0 && (previous_visible || next_visible)) {
            range_html = begin == end ? `${begin}` : `${begin} .. ${end}`
            files_html = `${files_html}, showing: ${range_html}`
        }

        paging_html += `<div class="info">${files_html}&nbsp;</div>`
    }

    // button previous page
    if (previous_visible) {
        paging_html += `<div id="btn-prev" class="action">[previous]&nbsp;</div>`
    }

    // button next page
    if (next_visible) {
        paging_html += `<div id="btn-next" class="action">[next]&nbsp;</div>`
    }

    // container end
    paging_html += "</div>"

    // update header and footer
    $("#paging-header").html(paging_html)

    // download archive
    $("#paging-footer").html(`<br>
    <a href="srv-dir-archive/${dir}" target="_blank">
    [download directory]</a>`)
}


// set HTML for the sub-directories of the current directory
function set_dirs(base_dir, dirs) {

    dir_html = ""

    if (dirs != 0)
        dirs.forEach(d => dir_html += to_dir_html(base_dir, d))

    $("#directories").html(dir_html)
}


// set HTML for the files of the page of the current directory
function set_files(base_dir, files) {

    file_html = ""

    if (files != 0) {

        begin = get_file_index()
        end = begin + get_page_size()

        for (i = begin; i < files.length && i < end; i++) {

            const file = files[i]
            file_html += to_file_html(base_dir, file)
        }
    }

    $("#files").html(file_html)
}


// compose HTML for a file (including download link)
function to_file_html(base_dir, file) {

    path    = `${base_dir}/${file}`
    content = to_content_html(path)
    number  = get_file_index() + document.file_count

    return `<div data-file="${path}" class="indent-1">
        ${content}
            <div class="width-3 action"> 
                <a href="srv-file/${path}" target="_blank">
                    <span class="inactive">${number}&nbsp;</span>
                    <span class="header section-3">${file}</span>
                </a>
            </div>
        </div>
        <br><br>`
}


// compose HTML for a directory
function to_dir_html(base_dir, dir) {

    key = `data-dir="${base_dir}/${dir}"`
    
    document.dir_count++

    return `<div ${key} class="container-1 back-1 action"> 
            <p>
                <span class="inactive">${document.dir_count}&nbsp;</span>
                <span class="header section-2">${dir}</span>
            </p>
        </div>`
}


// compose HTML for file content display (image, text, ...)
function to_content_html(path) {

    path = `srv-file/${path}`

    const key = `file-${++document.file_count}`

    content = ""

    // image
    if ((/\.(jpeg|jpg|png|gif)$/i).test(path))
    {
        content = `<img id="${key}" class="img-3" src="${path}"></img>`
    }
    // text
    else if ((/\.(md|txt|tex)$/i).test(path))
    {
        content = `<div class="back-1 width-3">
                <br>
                <p id="${key}" class="indent-1 clear">
                    <span class="info">Loading...</span>
                </p>
                <br>
            </div>`

        // deferred loading of the text content
        fetch(path)
            .then(response => response.text())
            .then(text => {

                element = $(`#${key}`)
                
                element.html(text)
            })
    }

    return content
}


// get file index
function get_file_index() {
    return parseInt(get_search_parameter("fileindex", 0))
}

// get page size
function get_page_size() {
    return parseInt(get_search_parameter("pagesize", 10))
}

// get path
function get_path() {
    return get_search_parameter("path", "$")
}