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
		'click .adhar_file_edit': '_onEditAdharCardFile',
		'change .adhar_file_upload': '_onAdharFileUploadChange',
		'click .adhar_file_browse': '_onBrowseAdharCardFile',
		'click .adhar_file_clear': '_onAdharFileClearClick',
		'click .passport_photo_edit': '_onEditPassportPhoto',
		'change .passport_photo_upload': '_onPassportPhotoUploadChange',
		'click .passport_photo_browse': '_onBrowsePassportPhoto',
		'click .passport_photo_clear': '_onPassportPhotoClearClick',
		'click .age_proof_edit': '_onEditAgeProof',
		'change .age_proof_upload': '_onAgeProofUploadChange',
		'click .age_proof_browse': '_onBrowseAgeProof',
		'click .age_proof_clear': '_onAgeProofClearClick',
		'click .address_proof_edit': '_onEditAddressProof',
		'change .address_proof_upload': '_onAddressProofUploadChange',
		'click .address_proof_browse': '_onBrowseAddressProof',
		'click .address_proof_clear': '_onAddressProofClearClick',
		'click .age_declaration_form_edit': '_onEditAgeDeclarationForm',
		'change .age_declaration_form_upload': '_onAgeDeclarationFormUploadChange',
		'click .age_declaration_form_browse': '_onBrowseAgeDeclarationForm',
		'click .age_declaration_form_clear': '_onAgeDeclarationFormClearClick',
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
			$('.voter_id_tab').addClass('d-none');
			// Show Birth place tab if Voter ID tab hides
			$('a.active').removeClass("active");
			$('div.active').removeClass("active");
			$('#tab-birthplace').addClass('active');
			$('#pane-birthplace').addClass('active');
			
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
    _onAdharFileUploadChange: function (ev) {
        if (!ev.currentTarget.files.length) {
            return;
        }
		var file_name = ev.target.files[0].name
		var $form = $(ev.currentTarget).closest('form');
		$form.find('.adhar_card_filename').val(file_name);
    },

 	/**
     * @private
     * @param {Event} ev
     */
	_onEditAdharCardFile: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.adhar_file_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
	_onBrowseAdharCardFile: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.adhar_file_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
    _onAdharFileClearClick: function (ev) {
		alert("clear")
        var $form = $(ev.currentTarget).closest('form');
        $form.find('.adhar_card_filename').val('');
		$form.find('.adhar_card_file_upload').val('');
    },

	/**
     * @private
     * @param {Event} ev
     */
    _onPassportPhotoUploadChange: function (ev) {
        if (!ev.currentTarget.files.length) {
            return;
        }
		var file_name = ev.target.files[0].name
		var $form = $(ev.currentTarget).closest('form');
		$form.find('.passport_photo_filename').val(file_name);
    },

 	/**
     * @private
     * @param {Event} ev
     */
	_onEditPassportPhoto: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.passport_photo_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
	_onBrowsePassportPhoto: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.passport_photo_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
    _onPassportPhotoClearClick: function (ev) {
        var $form = $(ev.currentTarget).closest('form');
        $form.find('.passport_photo_filename').val('');
		$form.find('.passport_photo_upload').val('');
    },

	/**
     * @private
     * @param {Event} ev
     */
    _onAgeProofUploadChange: function (ev) {
        if (!ev.currentTarget.files.length) {
            return;
        }
		var file_name = ev.target.files[0].name
		var $form = $(ev.currentTarget).closest('form');
		$form.find('.age_proof_filename').val(file_name);
    },

 	/**
     * @private
     * @param {Event} ev
     */
	_onEditAgeProof: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.age_proof_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
	_onBrowseAgeProof: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.age_proof_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
    _onAgeProofClearClick: function (ev) {
        var $form = $(ev.currentTarget).closest('form');
        $form.find('.age_proof_filename').val('');
		$form.find('.age_proof_upload').val('');
    },

	/**
     * @private
     * @param {Event} ev
     */
    _onAddressProofUploadChange: function (ev) {
        if (!ev.currentTarget.files.length) {
            return;
        }
		var file_name = ev.target.files[0].name
		var $form = $(ev.currentTarget).closest('form');
		$form.find('.address_proof_filename').val(file_name);
    },

 	/**
     * @private
     * @param {Event} ev
     */
	_onEditAddressProof: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.address_proof_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
	_onBrowseAddressProof: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.address_proof_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
    _onAddressProofClearClick: function (ev) {
        var $form = $(ev.currentTarget).closest('form');
        $form.find('.address_proof_filename').val('');
		$form.find('.address_proof_upload').val('');
    },

	/**
     * @private
     * @param {Event} ev
     */
    _onAgeDeclarationFormUploadChange: function (ev) {
        if (!ev.currentTarget.files.length) {
            return;
        }
		var file_name = ev.target.files[0].name
		var $form = $(ev.currentTarget).closest('form');
		$form.find('.age_declaration_form_filename').val(file_name);
    },

 	/**
     * @private
     * @param {Event} ev
     */
	_onEditAgeDeclarationForm: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.age_declaration_form_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
	_onBrowseAgeDeclarationForm: function (ev) {
    	ev.preventDefault();
        $(ev.currentTarget).closest('form').find('.age_declaration_form_upload').trigger('click');
 	},

 	/**
     * @private
     * @param {Event} ev
     */
    _onAgeDeclarationFormClearClick: function (ev) {
        var $form = $(ev.currentTarget).closest('form');
        $form.find('.age_declaration_form_filename').val('');
		$form.find('.age_declaration_form_upload').val('');
    },

});
});
