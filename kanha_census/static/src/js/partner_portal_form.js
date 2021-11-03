odoo.define('kanha_census.partner_portal_form', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var Dialog = require('web.Dialog');

publicWidget.registry.portalPartnerDetails = publicWidget.Widget.extend({
    selector: '.o_portal_partner_details',
    events: {
		'change select[name="change_voter_id_address"]': '_onVoterAddressChange',
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
		//'click .add_vehicle_line': '_onAddLine',
		
		'change select[name="birth_country_id"]': '_onBirthCountryChange',
		'change select[name="country_id"]': '_onCountryChange',
    },
 
    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
		this.$birth_state = this.$('select[name="birth_state_id"]');
        this.$birth_stateOptions = this.$birth_state.filter(':enabled').find('option:not(:first)');
        this._adaptBirthAddressForm();
		this.$state = this.$('select[name="state_id"]');
        this.$stateOptions = this.$state.filter(':enabled').find('option:not(:first)');
        this._adaptAddressForm();

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
    _onVoterAddressChange: function () {
		var voter_address_change = this.$('select[name="change_voter_id_address"]');
		if(voter_address_change.val() == 'Yes'){
			$('.voter_id_tab').removeClass('d-none');
			
			/*Add or Remove Disabled property for the fields is to 
			Avoid Mandatory check if the tab is hide*/
			$('#existing_voter_id_number_id').removeAttr('disabled');
			$('#voter_country_id').removeAttr('disabled');
			$('#voter_state_id').removeAttr('disabled');
			$('#assembly_constituency_id').removeAttr('disabled');
			$('#house_number_id').removeAttr('disabled');
			$('#locality_id').removeAttr('disabled');
			$('#town_id').removeAttr('disabled');
			$('#post_office_id').removeAttr('disabled');
			$('#zip_id').removeAttr('disabled');
			$('#district_id').removeAttr('disabled');
		}
		else{
			var is_voter_tab_active = $('a.voter_id_tab').hasClass('active');
			$('.voter_id_tab').addClass('d-none');
			
			$('#existing_voter_id_number_id').attr('disabled', true);
			$('#voter_country_id').attr('disabled', true);
			$('#voter_state_id').attr('disabled', true);
			$('#assembly_constituency_id').attr('disabled', true);
			$('#house_number_id').attr('disabled', true);
			$('#locality_id').attr('disabled', true);
			$('#town_id').attr('disabled', true);
			$('#post_office_id').attr('disabled', true);
			$('#zip_id').attr('disabled', true);
			$('#district_id').attr('disabled', true);
			
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

    /**
     * @private
     */
    _adaptBirthAddressForm: function () {
        var $birth_country = this.$('select[name="birth_country_id"]');
        var birth_countryID = ($birth_country.val() || 0);
        this.$birth_stateOptions.detach();
        var $birth_displayedState = this.$birth_stateOptions.filter('[data-country_id=' + birth_countryID + ']');
        var nb = $birth_displayedState.appendTo(this.$birth_state).show().length;
        //this.$state.parent().toggle(nb >= 1);
    },

	/**
     * @private
     */
    _onBirthCountryChange: function () {
        this._adaptBirthAddressForm();
    },

    /**
     * @private
     */
    _adaptAddressForm: function () {
        var $country = this.$('select[name="country_id"]');
        var countryID = ($country.val() || 0);
        this.$stateOptions.detach();
        var $displayedState = this.$stateOptions.filter('[data-country_id=' + countryID + ']');
        var nb = $displayedState.appendTo(this.$state).show().length;
        //this.$state.parent().toggle(nb >= 1);
    },

	/**
     * @private
     */
    _onCountryChange: function () {
        this._adaptAddressForm();
    },


});
});
