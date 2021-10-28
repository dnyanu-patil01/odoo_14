odoo.define('kanha_census.partner_portal_form', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var Dialog = require('web.Dialog');

publicWidget.registry.portalPartnerDetails = publicWidget.Widget.extend({
    selector: '.o_portal_partner_details',
    events: {
		'change select[name="application_type"]': '_onApplicationTypeChange',
		'change #passport_photo': '_onPassportPhotoChange',
		'change select[name="citizenship"]': '_onCitizenshipChange',
		
		'click .adhar_file_edit': '_onBrowseFile',
		'change .adhar_file_upload': '_onFileUploadChange',
		'click .adhar_file_browse': '_onBrowseFile',
		'click .adhar_file_clear': '_onClearFile',
		
		'click .adhar_file_back_side_edit': '_onBrowseFile',
		'change .adhar_file_back_side_upload': '_onFileUploadChange',
		'click .adhar_file_back_side_browse': '_onBrowseFile',
		'click .adhar_file_back_side_clear': '_onClearFile',
		
		'click .passport_photo_edit': '_onBrowseFile',
		'change .passport_photo_upload': '_onFileUploadChange',
		'click .passport_photo_browse': '_onBrowseFile',
		'click .passport_photo_clear': '_onClearFile',
		
		'click .age_proof_edit': '_onBrowseFile',
		'change .age_proof_upload': '_onFileUploadChange',
		'click .age_proof_browse': '_onBrowseFile',
		'click .age_proof_clear': '_onClearFile',
		
		'click .address_proof_edit': '_onBrowseFile',
		'change .address_proof_upload': '_onFileUploadChange',
		'click .address_proof_browse': '_onBrowseFile',
		'click .address_proof_clear': '_onClearFile',
		
		'click .age_declaration_form_edit': '_onBrowseFile',
		'change .age_declaration_form_upload': '_onFileUploadChange',
		'click .age_declaration_form_browse': '_onBrowseFile',
		'click .age_declaration_form_clear': '_onClearFile',
    },
 
    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
        return def;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

	/**
     * Show Voter ID details if selected Application type is Transfer Application
     *
     * @private
     */
    _onApplicationTypeChange: function () {
       var application_type = this.$('select[name="application_type"]');
		if(application_type.val() == 'Transfer Application'){
			$('.voter_id_tab').removeClass('d-none');
		}
		else{
			var is_voter_tab_active = $('a.voter_id_tab').hasClass('active');
			$('.voter_id_tab').addClass('d-none');
			// Show Birth place tab if Voter ID tab hides
			if(is_voter_tab_active)
			{
				$('a.active').removeClass("active");
				$('div.active').removeClass("active");
				$('#tab-birthplace').addClass('active');
				$('#pane-birthplace').addClass('active');
			}
		}
    },

	/**
     * Restrict the size of a file upload
     *
     * @private
     */
	_onPassportPhotoChange: function (ev) {
		var file = ev.target.files[0];
	  	var fileSize = file.size / 1024 / 1024; // in MiB
  		if (fileSize > 2) {
			Dialog.alert(null, "File is too big. File size cannot exceed 2MB.");
        	document.getElementById("passport_photo").value = "";
		}
	},

	/**
     * Show Passport Number field if selected Citizenship is Overseas
     *
     * @private
     */
	_onCitizenshipChange: function () {
       var citizenship = this.$('select[name="citizenship"]');
		if(citizenship.val() == 'Overseas'){
			$('.passport_field').removeClass('d-none');
		}
		else{
			$('.passport_field').addClass('d-none');
		}
    },

 	/**
     * @private
     * @param {Event} ev
     */
	_onBrowseFile: function (ev) {
		ev.preventDefault();
		var fileupload = $(ev.target).attr('fileupload')
        $(ev.currentTarget).closest('form').find('.'+fileupload).trigger('click');
 	},

    /**
     * @private
     * @param {Event} ev
     */
    _onFileUploadChange: function (ev) {
        if (!ev.currentTarget.files.length) {
            return;
        }
		var file_name = ev.target.files[0].name
		var $form = $(ev.currentTarget).closest('form');
		var filename_input = $(ev.target).attr('filename_input')
		$form.find('.'+filename_input).val(file_name);
    },
 	
 	/**
     * @private
     * @param {Event} ev
     */
    _onClearFile: function (ev) {
		var fileupload_input = $(ev.target).attr('fileupload_input')
		var filename_input = $(ev.target).attr('filename_input')
        var $form = $(ev.currentTarget).closest('form');
        $form.find('.'+filename_input).val('');
		$form.find('.'+fileupload_input).val('');
    },

});
});
