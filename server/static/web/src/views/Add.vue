<template>
    <div class="container">
        <div class="mb-3">
            <label for="exampleFormControlInput1" class="form-label">Email address</label>
            <input type="email" class="form-control" id="exampleFormControlInput1" placeholder="name@example.com">
        </div>
        <div class="mb-3">
            <label for="DiagFileInput" class="form-label">DiagFile</label>
            <input id="DiagFileInput" class="form-control" ref="DiagFileInput" @change=handleDiagFileChange() type="file" accept=".tbz2">
        </div>
        <div class="mb-3">
            <label for="AedToolKitInput" class="form-label">AedToolKit Export</label>
            <input id="AedToolKitInput" class="form-control" ref="AedToolKitInput" @change=handleAedToolKitChange() type="file" accept=".bz2">
        </div>
        <!-- <button type="submit" :disabled="!(AedToolKitFile && DiagFile)" @click="processSubmit" class="btn btn-primary w-100">Process</button> -->
        <button type="submit" @click="processSubmit" class="btn btn-primary w-100">Process</button>
        <div class="container-xs">
            <table v-if="process_logs.length > 0" class="table mt-2">
                <tr v-for="process_log in process_logs">
                    <td v-html="process_log"></td>
                </tr>
            </table>
        </div>
    </div>
    
</template>

<script setup>

import { onMounted, ref } from 'vue'
const AedToolKitInput = ref(null)
const AedToolKitFile = ref()
const DiagFileInput = ref(null)
const DiagFile = ref()
const process_logs = ref([])

function handleAedToolKitChange() {
    AedToolKitFile.value = AedToolKitInput.value.files
}

function handleDiagFileChange() {
    DiagFile.value = DiagFileInput.value.files
}

function uploadFile(file, project_id){
    return new Promise((resolve) => {
        let formData = new FormData
        formData.append('file', file)
        formData.append('project_id', project_id)
        fetch( '/aed_reviewer/api/aed/upload', {
        method: 'POST',
        body: formData
        })
        .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('File upload failed');
        }
        })
        .then((data) => {
            if (!(data.success)) throw new Error('File upload failed');
            resolve(true)
        })
        .catch(error => {
        console.error('Error uploading file:', error);
        });
    })
}

function create_project(){
    return new Promise((resolve) => {
        var project_id = null
        fetch('/aed_reviewer/api/aed/add_project')
        .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Add Project failed');
        }
        })
        .then((data) => {
            if (!(data.success)) throw new Error('Add Project failed');
            resolve(data.project_id)
        })
    })
}

function uncompress_project(project_id){
    return new Promise((resolve) => {
        fetch('/aed_reviewer/api/'+project_id+'/uncompress')
        .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Uncompress failed');
        }
        })
        .then((data) => {
            if (!(data.success)) throw new Error('Uncompress failed');
            resolve(true)
        })
    })
}

function parse_project(project_id){
    return new Promise((resolve) => {
        fetch('/aed_reviewer/api/'+project_id+'/parse')
        .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Parsing failed');
        }
        })
        .then((data) => {
            if (!(data.success)) throw new Error('Parsing failed');
            resolve(true)
        })
    })
}


async function processSubmit() {


    // console.log(AedToolKitFile.value[0])
    // console.log(DiagFile.value[0])
    
    process_logs.value.push('Creating Project ...')
    const project_id = await create_project()
    process_logs.value.push('Done: Project: '+project_id)
    
    console.log('Uploading AedToolKitFile ...')
    process_logs.value.push('Uploading AedToolKitFile')
    if (await uploadFile(AedToolKitFile.value[0], project_id) != true) process_logs.value.push("Error")
    process_logs.value.push('Done')
    process_logs.value.push('Uploading DiagFile ...')
    console.log('Uploading DiagFile')
    if (await uploadFile(DiagFile.value[0], project_id) != true) process_logs.value.push("Error")
    process_logs.value.push('Done')
    process_logs.value.push('Uncompressing ...')
    console.log('Uncompressing')
    if (await uncompress_project(project_id) != true) process_logs.value.push("Error Uncompressing")
    process_logs.value.push('Done')
    process_logs.value.push('Parsing ...')
    console.log('Parsing')
    if (await parse_project(project_id) != true) process_logs.value.push("Error Parsing")
    process_logs.value.push('Done')
    console.log('Done')
    process_logs.value.push('<a href=\"/aed_reviewer/'+project_id+'/protection-groups" class="btn btn-primary">'+project_id+'</a>')
    
}


function upload(file) {
  let xhr = new XMLHttpRequest();

  // listen for upload progress
  xhr.upload.onprogress = function(event) {
    let percent = Math.round(100 * event.loaded / event.total);
    console.log(`File is ${percent} uploaded.`);
  };

  // handle error
  xhr.upload.onerror = function() {
    console.log(`Error during the upload: ${xhr.status}.`);
  };

  // upload completed successfully
  xhr.onload = function() {
    console.log('Upload completed successfully.');
  };

  xhr.open('POST', '/aed_reviewer/api/aed/upload');
  xhr.send(file);
}


async function fetchForm(form, options = {}) 
{
    var method = options.method || form.getAttribute('method') || 'get';
    var action = options.url || form.getAttribute('action');
    var data   = new FormData(form);
    var xhr    = new XMLHttpRequest(); 

    return new Promise(function(success, failure) 
    {
        xhr.responseType = 'blob';
        xhr.onreadystatechange = function() 
        {
            if (xhr.readyState != 4) { // done
               return; 
            }

            var response = new Response(xhr.response, { 
                url         : xhr.responseURL, 
                status      : xhr.status, 
                statusText  : xhr.statusText
            });
            
            success(response);
        }        

        xhr.addEventListener('error', () => 
        { 
            failure( new TypeError('Failed to fetch') ) 
        });

        if (options.progress) {
            xhr.addEventListener('progress', options.progress);
        }

        xhr.open(method, action, true);
        xhr.send(data);
    });
}

</script>