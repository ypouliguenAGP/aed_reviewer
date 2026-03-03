<template>
    <div class="container">
        <!-- AED ID field -->
        <div class="mb-3">
            <label for="aedIdInput" class="form-label">AED ID</label>
            <input type="text" class="form-control" id="aedIdInput" placeholder="aed-...." v-model="aed_id">
        </div>
        <!-- Password field -->
        <div class="mb-3">
            <label for="passwordInput" class="form-label">Password</label>
            <input type="password" class="form-control" id="passwordInput" placeholder="" v-model="password">
        </div>
        
        <!-- <button type="submit" :disabled="!(AedToolKitFile && DiagFile)" @click="processSubmit" class="btn btn-primary w-100">Process</button> -->
        <button
            type="submit"
            :disabled="password.length !== 44 || aed_id.length !== 12"
            @click="processSubmit"
            class="btn btn-primary w-100"
        >
            Access
        </button>
    </div>
    
</template>

<script setup>

import { onMounted, ref } from 'vue'
const aed_id = ref('')
const password = ref('')

function processSubmit() {
    // Here you can handle the form submission, e.g., send data to the server
    console.log('AED ID:', aed_id.value);
    // Using the Fetch API, Validate AED id and password using the endpoint /api/aed/validation
    fetch('/aed_reviewer/api/aed/validation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            aed_id: aed_id.value,
            aed_password: password.value,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.replace(`/aed_reviewer/${aed_id.value}/protection-groups`);
            // Redirect to AED dashboard or another page if needed
        } else {
            alert('Invalid AED ID or password. Please try again.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

</script>