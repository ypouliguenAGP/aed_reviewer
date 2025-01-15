<script>
export default {
  name: 'AlertDefault',
  props: {
    alerts: Object,
  },
  data(){
    return{
       
    }
  },
  methods:{

  }
}
</script>
<template>
  <div >
  <!-- Modal -->
  <div class="modal fade show" 
   tabindex="-1" aria-labelledby="exampleModalLabel" aria-modal="true" role="dialog" 
   style="display:block">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          
          <button type="button" class="btn-close" ></button>
        </div>
        <div class="modal-body">
         Alerts
        </div>
        <div class="modal-footer">
          <button type="button" :class="'btn btn-'+variant" >Close</button>
        </div>
      </div>
    </div>
  </div>
  </div>
  </template>