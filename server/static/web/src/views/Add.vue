<template>
    <div class="container">
        <div class="mb-3">
            <label for="exampleFormControlInput1" class="form-label">Email address</label>
            <input type="email" class="form-control" id="exampleFormControlInput1" placeholder="name@example.com">
        </div>
        <div class="mb-3">
            <label for="formFile" class="form-label">DiagFile</label>
            <input class="form-control" ref="DiagFileInput" @change=handleDiagFileChange() type="file" accept=".tbz2" id="formFile">
        </div>
        <div class="mb-3">
            <label for="formFile" class="form-label">AedToolKit Export</label>
            <input class="form-control" ref="AedToolKitInput" @change=handleAedToolKitChange() type="file" accept=".bz2"id="formFile">
        </div>
        <button type="submit" :disabled="!(AedToolKitInput && DiagFileInput)" @click="processSubmit" class="btn btn-primary w-100">Process</button>
    </div>
    
</template>

<script setup>

import { onMounted, ref } from 'vue'
const AedToolKitInput = ref(null)
const AedToolKitFile = ref()
const DiagFileInput = ref(null)
const DiagFile = ref()

function handleAedToolKitChange() {
    AedToolKitFile.value = AedToolKitInput.value.files
}

function handleDiagFileChange() {
    DiagFile.value = DiagFileInput.value.files
}

function uploadFile(formData){
    fetch( 'http://localhost:5000/aed_reviewer/api/aed/add', {
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
    .then(data => {
    console.log('Server response:', data);
    })
    .catch(error => {
    console.error('Error uploading file:', error);
    });
}


function processSubmit() {
    console.log('Uploading %s', AedToolKitFile.value[0])
    const formData = new FormData();
    formData.append('file', AedToolKitFile.value[0], AedToolKitFile.value[0].name);
    formData.append('file', DiagFile.value[0], DiagFile.value[0].name);
    uploadFile(formData)
    console.log(AedToolKitFile.value[0])
    console.log(DiagFile.value[0])
    // and do other things...
}

</script>