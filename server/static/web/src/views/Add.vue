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
const key = ref('')

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
        // Create a variable to store upload progress
        const uploadProgress = ref(0);

        // Track upload progress
        formData.get('file') && fetch('/aed_reviewer/api/aed/upload', {
            method: 'POST',
            body: formData,
            // Use XMLHttpRequest for progress tracking
            signal: undefined // placeholder, fetch does not support progress natively
        });

        // Use XMLHttpRequest for progress tracking
        let xhr = new XMLHttpRequest();
        xhr.upload.onprogress = function(event) {
            if (event.lengthComputable) {
            uploadProgress.value = Math.round((event.loaded / event.total) * 100);
            console.log(`File is ${uploadProgress.value}% uploaded.`);
            process_logs.value[process_logs.value.length - 1] = process_logs.value[process_logs.value.length - 1].split(' - ')[0] + ` - (${uploadProgress.value}%)`
            }
        };
        xhr.open('POST', '/aed_reviewer/api/aed/upload');
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
            resolve(true);
            } else {
            console.error('Error uploading file:', xhr.statusText);
            }
        };
        xhr.onerror = function() {
            console.error('Error uploading file:', xhr.statusText);
        };
        xhr.send(formData);
        return;
        
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
            return response.json().then(data => {
                key.value = data.key
                return data
            });
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

function parse_statusdump(project_id){
    return new Promise((resolve) => {
        fetch('/aed_reviewer/api/'+project_id+'/statusdump_parse')
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
    
    console.log('Uploading AedToolKitFile')
    process_logs.value.push('Uploading AedToolKitFile - (0%)')
    if (await uploadFile(AedToolKitFile.value[0], project_id) != true) process_logs.value.push("Error")
    process_logs.value.push('Done')
    process_logs.value.push('Uploading DiagFile - (0%)')
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
    process_logs.value.push('StatusDump Parsing ...')
    console.log('Parsing')
    if (await parse_statusdump(project_id) != true) process_logs.value.push("Error Parsing")
    process_logs.value.push('Done')
    console.log('Done')
    // print Key
    process_logs.value.push('Project Key: '+key.value)
    process_logs.value.push('<a href=\"/aed_reviewer/'+project_id+'/protection-groups" class="btn btn-primary">'+project_id+'</a>')
    
}


</script>