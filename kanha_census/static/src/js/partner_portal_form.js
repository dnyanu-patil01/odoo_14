odoo.define('kanha_census.partner_portal_form', function (require) {
'use strict';

var core = require('web.core');
var time = require('web.time');
var ajax = require('web.ajax');
var publicWidget = require('web.public.widget');
const dom = require('web.dom');
var Dialog = require('web.Dialog');
var _t = core._t;


publicWidget.registry.portalPartnerDetails = publicWidget.Widget.extend({
    selector: '.o_portal_partner_details',
    events: {
		'change select[name="change_voter_id_address"]': '_onVoterAddressChange',
		'change select[name="citizenship"]': '_onCitizenshipChange',
		'change select[name="application_type"]': '_onChangeVoterApplicationType',
		'change select[name="already_have_kanha_voter_id"]': '_onChangeAlreadyHaveKanhaVoterID',
		'change select[name="need_new_kanha_voter_id"]': '_onChangeNeedNewKanhaVoterID',
		// Adhar File Front upload
		'click .adhar_file_edit': '_onBrowseFile',
		'change .adhar_file_upload': '_onFileUploadChange',
		'click .adhar_file_browse': '_onBrowseFile',
		'click .adhar_file_clear': '_onClearFile',
		// Adhar File Back upload
		'click .adhar_file_back_side_edit': '_onBrowseFile',
		'change .adhar_file_back_side_upload': '_onFileUploadChange',
		'click .adhar_file_back_side_browse': '_onBrowseFile',
		'click .adhar_file_back_side_clear': '_onClearFile',
		// Adhar File upload
		'click .age_proof_edit': '_onBrowseFile',
		'change .age_proof_upload': '_onFileUploadChange',
		'click .age_proof_browse': '_onBrowseFile',
		'click .age_proof_clear': '_onClearFile',
		// Address File upload
		'click .address_proof_edit': '_onBrowseFile',
		'change .address_proof_upload': '_onFileUploadChange',
		'click .address_proof_browse': '_onBrowseFile',
		'click .address_proof_clear': '_onClearFile',
		// Passport Photot upload
		'click .passport_photo_edit': '_onBrowseFile',
		'change .passport_photo_upload': '_onUploadPassportPhoto',
		'click .passport_photo_browse': '_onBrowseFile',
		'click .passport_photo_clear': '_onClearFile',
		// Kanha voter ID image upload
		'click .kanha_voter_id_image_browse': '_onBrowseFile',
		'change .kanha_voter_id_image_upload': '_onUploadKanhaVoterIdImage',
		'click .kanha_voter_id_image_edit': '_onBrowseFile',
		'click .kanha_voter_id_image_clear': '_onClearFile',
		// voter ID File upload
		'click .voter_id_file_browse': '_onBrowseFile',
		'change .voter_id_file_upload': '_onFileUploadChange',
		'click .voter_id_file_edit': '_onBrowseFile',
		'click .voter_id_file_clear': '_onClearFile',
		// Declaration Form upload
		'click .declaration_form_edit': '_onBrowseFile',
		'change .declaration_form_upload': '_onUploadDeclarationForm',
		'click .declaration_form_browse': '_onBrowseFile',
		'click .declaration_form_clear': '_onClearFile',
		// Country selection
		'change select[name="birth_country_id"]': '_onBirthCountryChange',
		'change select[name="country_id"]': '_onCountryChange',
		// Vehicle actions
		'click .vehicle_add_new': '_onShowVehicleModal',
		'click .vehicle_edit_new': '_onShowVehicleModal',
		'click .vehicle_edit_exist': '_onShowVehicleModal',
		'click .save_vehicle_line': '_onSaveVehicle',
		'click .vehicle_clear': '_onDeleteVehicleLine',
		// File input fields
		'keypress #adhar_card_file_front': '_onRestrictInput',
		'keydown #adhar_card_file_front': '_onRestrictInput',
		'keypress #adhar_card_file_back': '_onRestrictInput',
		'keydown #adhar_card_file_back': '_onRestrictInput',
		'keypress #passport_photo_file': '_onRestrictInput',
		'keydown #passport_photo_file': '_onRestrictInput',
		'keypress #age_proof_file': '_onRestrictInput',
		'keydown #age_proof_file': '_onRestrictInput',
		'keypress #address_proof_file': '_onRestrictInput',
		'keydown #address_proof_file': '_onRestrictInput',
		'keypress #kanha_voter_id_image_filename_field': '_onRestrictInput',
		'keydown #kanha_voter_id_image_filename_field': '_onRestrictInput',
		'keypress #voter_id_file_filename_field': '_onRestrictInput',
		'keydown #voter_id_file_filename_field': '_onRestrictInput',
		'keypress #declaration_form_filename_field': '_onRestrictInput',
		'keydown #declaration_form_filename_field': '_onRestrictInput',
		// Form submit
		'click .family_website_form_submit': '_onSubmitForm',
    },
 
    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
		this.$birthState = this.$('select[name="birth_state_id"]');
        this.$birthStateOptions = this.$birthState.filter(':enabled').find('option:not(:first)');
        this._adaptBirthStateAddressForm();
		this.$state = this.$('select[name="state_id"]');
        this.$stateOptions = this.$state.filter(':enabled').find('option:not(:first)');
        this._adaptAddressForm();

        return def;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
	
	/**
     * Restricts input on File name fields
     *
     * @private
     */
	_onRestrictInput: function (ev) {
		 ev.preventDefault();
	},
	
	/**
     * Show/Hide Voter ID details based on selected value of Change Voter ID address
     *
     * @private
     */
    _onVoterAddressChange: function (ev) {
		document.getElementById("application_type_field").value = "";
        $(ev.currentTarget).closest('form').find('select[name="application_type"]').trigger('change');
	
		var voter_is_there = this.$('select[id="already_have_kanha_voter_id_field"]');
		var voter_address_change = this.$('select[name="change_voter_id_address"]');
		if(voter_address_change.val() == 'Yes'){
			$('.voter_id_tab').removeClass('d-none');
			
			/*Set Required attribute for the fields to 
			validate Mandatory fields when this tab is active*/
			$('#existing_voter_id_number_field').attr('required', true);
			$('#voter_country_id').attr('required', true);
			$('#voter_state_id').attr('required', true);
			$('#assembly_constituency_field').attr('required', true);
			$('#house_number_field').attr('required', true);
			$('#locality_field').attr('required', true);
			$('#town_field').attr('required', true);
			$('#post_office_field').attr('required', true);
			$('#zip_field').attr('required', true);
			$('#district_field').attr('required', true);
			// show Voter Application Type field
			$('.voter_application_type').removeClass('d-none');
			$('#application_type_field').attr('required', true);

			var transfer_application = '<option value="Transfer Application">Transfer Application</option>'
			if(voter_is_there.val() == 'Yes'){
				$('#application_type_field').empty().append(transfer_application);
			}
			
			/*$('.kanha_voter_id_number').addClass('d-none');
			$('#kanha_voter_id_number_field').removeAttr('required');*/
		
		}
		else{
			
			/*$('.kanha_voter_id_number').removeClass('d-none');
			$('#kanha_voter_id_number_field').attr('required', true);*/
			var is_voter_tab_active = $('a.voter_id_tab').hasClass('active');
			$('.voter_id_tab').addClass('d-none');
			
			/*Remove Required attribute for the fields to 
			validate Mandatory fields when this tab is hide*/
			
			$('#existing_voter_id_number_field').removeAttr('required');
			$('#voter_country_id').removeAttr('required');
			$('#voter_state_id').removeAttr('required');
			$('#assembly_constituency_field').removeAttr('required');
			$('#house_number_field').removeAttr('required');
			$('#locality_field').removeAttr('required');
			$('#town_field').removeAttr('required');
			$('#post_office_field').removeAttr('required');
			$('#zip_field').removeAttr('required');
			$('#district_field').removeAttr('required');
			
			$('.voter_application_type').addClass('d-none');
			$('#application_type_field').removeAttr('required');
			
			/*Show Kanha Address tab if Existing Voter ID tab hides when Existing Voter ID tab in active*/
			if(is_voter_tab_active)
			{
				$('a.active').removeClass("active");
				$('div.active').removeClass("active");
				$('#tab-kanha').addClass('active');
				$('#pane-kanha').addClass('active');
			}
		}
    },


	/**
     * Show/Hide fields based on selected value of Already have kanha voter ID
     *
     * @private
     */
    _onChangeAlreadyHaveKanhaVoterID: function (ev) {
		// Hide the fields and value based on the super parent field visibility
		document.getElementById("need_new_kanha_voter_id_field").value = "";
        $(ev.currentTarget).closest('form').find('select[name="need_new_kanha_voter_id"]').trigger('change');

		var already_have_kanha_voter_id = this.$('select[name="already_have_kanha_voter_id"]');
		if(already_have_kanha_voter_id.val() == 'Yes'){
			
			// Hide Need New Kanha Voter ID field
			$('.need_new_kanha_voter_id').addClass('d-none');
			$('#need_new_kanha_voter_id_field').removeAttr('required');
			
			// Show Kanha Voter ID number and Kanha Voter ID image fields and add required attribute
			$('.kanha_voter_id_number').removeClass('d-none');
			$('#kanha_voter_id_number_field').attr('required', true);
			
			$('.kanha_voter_id_image').removeClass('d-none');
			$('#kanha_voter_id_image_field').attr('required', true);
			
			$('.change_voter_id_address').removeClass('d-none');
			
		}
		else if(already_have_kanha_voter_id.val() == 'No'){
			
			// Hide Kanha Voter ID number and Kanha Voter ID image fields and remove required attribute			
			$('.kanha_voter_id_number').addClass('d-none');
			$('#kanha_voter_id_number_field').removeAttr('required');
			//document.getElementById("kanha_voter_id_number_field").value = "";
			
			$('.kanha_voter_id_image').addClass('d-none');
			$('#kanha_voter_id_image_field').removeAttr('required');
			//document.getElementById("kanha_voter_id_image_field").value = "";
			//document.getElementById("kanha_voter_id_image_filename_field").value = "";
			
			// Show Need New Kanha Voter ID field
			$('.need_new_kanha_voter_id').removeClass('d-none');
			$('#need_new_kanha_voter_id_field').attr('required', true);
			
			$('.change_voter_id_address').addClass('d-none');

		}
		else{
			
			

			// Hide Need New Kanha Voter ID field
			$('.need_new_kanha_voter_id').addClass('d-none');
			$('#need_new_kanha_voter_id_field').removeAttr('required');

			// Hide Kanha Voter ID number and Kanha Voter ID image fields and remove required attribute			
			$('.kanha_voter_id_number').addClass('d-none');
			$('#kanha_voter_id_number_field').removeAttr('required');
			
			$('.kanha_voter_id_image').addClass('d-none');
			$('#kanha_voter_id_image_field').removeAttr('required');
			
			$('.change_voter_id_address').addClass('d-none');
		}
    },

	/**
     * Show/Hide fields based on selected value of Need new Kanha voter ID
     *
     * @private
     */
    _onChangeNeedNewKanhaVoterID: function (ev) {
		// Hide the fields and value based on the super parent field visibility
		document.getElementById("application_type_field").value = "";
        $(ev.currentTarget).closest('form').find('select[name="application_type"]').trigger('change');

		var need_new_kanha_voter_id = this.$('select[name="need_new_kanha_voter_id"]');
		if(need_new_kanha_voter_id.val() == 'Yes'){
			// show Voter Application Type field
			$('.voter_application_type').removeClass('d-none');
			$('#application_type_field').attr('required', true);
			var new_application = '<option value="New Application">New Application</option>'
			$('#application_type_field').empty().append(new_application);
		}
		else{
			// Hide Voter Application Type field
			$('.voter_application_type').addClass('d-none');
			$('#application_type_field').removeAttr('required');
		}
    },

	/**
     * Show/Hide fields based on Selected Application type
     *
     * @private
     */
    _onChangeVoterApplicationType: function () {
		var application_type = this.$('select[name="application_type"]');
		if(application_type.val() == 'New Application'){
			
			// Show Declaration Form field
			$('.declaration_form').removeClass('d-none');
			$('#declaration_form_field').attr('required', true);
			
			// Hide Existing Voter ID number and Voter ID file
			$('.existing_voter_id_number').addClass('d-none');
			$('#existing_voter_id_number_field').removeAttr('required');
			//document.getElementById("existing_voter_id_number_field").value = "";
			
			$('.voter_id_file').addClass('d-none');
			$('#voter_id_file_field').removeAttr('required');
			//document.getElementById("voter_id_file_field").value = "";
			//document.getElementById("voter_id_file_filename_field").value = "";
			
		}
		else if(application_type.val() == 'Transfer Application'){
			// Hide Declaration Form field
			$('.declaration_form').addClass('d-none');
			$('#declaration_form_field').removeAttr('required');
			//document.getElementById("declaration_form_field").value = "";
			//document.getElementById("declaration_form_filename_field").value = "";
			
			// Show Existing Voter ID number and Voter ID file
			$('.existing_voter_id_number').removeClass('d-none');
			$('#existing_voter_id_number_field').attr('required', true);
			
			$('.voter_id_file').removeClass('d-none');
			$('#voter_id_file_field').attr('required', true);
			
		}
		else{
			
			// Hide Existing Voter ID number and Voter ID file
			$('.existing_voter_id_number').addClass('d-none');
			$('#existing_voter_id_number_field').removeAttr('required');
			//document.getElementById("existing_voter_id_number_field").value = "";

			$('.voter_id_file').addClass('d-none');
			$('#voter_id_file_field').removeAttr('required');
			//document.getElementById("voter_id_file_field").value = "";
			//document.getElementById("voter_id_file_filename_field").value = "";
			
			// Hide Declaration Form field
			$('.declaration_form').addClass('d-none');
			$('#declaration_form_field').removeAttr('required');
			//document.getElementById("declaration_form_field").value = "";
			//document.getElementById("declaration_form_filename_field").value = "";
		}
    },

	/**
     * Show Passport Number and Hide Kanha Voter ID tab if selected Citizenship is Overseas
     *
     * @private
     */
	_onCitizenshipChange: function () {
		var citizenship = this.$('select[name="citizenship"]');
		if(citizenship.val() == 'Overseas'){
			// Show Passport Number and add Required attribute
			$('.passport_field').removeClass('d-none');
			$('#passport_number_input').attr('required', true);
			
			// Remove Mandatory validation
			$('#aadhaar_card_number_field').removeAttr('required');
			$('#adhar_card_file_front').removeAttr('required');
			$('#adhar_card_file_back').removeAttr('required');
			
			// Show Kanha Address tab if Kanha Voter ID tab hides when Voter ID tab in active
			var is_kanha_voter_tab_active = $('a#tab-kanha_voter_id').hasClass('active');
			// Hide Kanha Voter ID tab
			$('#tab-kanha_voter_id').addClass('d-none');
			if(is_kanha_voter_tab_active)
			{
				$('a.active').removeClass("active");
				$('div.active').removeClass("active");
				$('#tab-kanha').addClass('active');
				$('#pane-kanha').addClass('active');
				$('#pane-kanha').addClass('show');
			}
			
			$('#birth_country_id_field').removeAttr('required');
			$('#birth_state_id_field').removeAttr('required');
			$('#birth_district_field').removeAttr('required');
			$('#birth_town_field').removeAttr('required');
			$('#change_voter_id_address_field').removeAttr('required');
			$('#voter_id_number_field').removeAttr('required');
			$('#already_have_kanha_voter_id_field').removeAttr('required');
			$('#kanha_voter_id_number_field').removeAttr('required');
			$('#kanha_voter_id_image_field').removeAttr('required');
			$('#kanha_voter_id_image_filename_field').removeAttr('required');
			$('#need_new_kanha_voter_id_field').removeAttr('required');
			$('#application_type_field').removeAttr('required');
			$('#existing_voter_id_number_field').removeAttr('required');
			$('#voter_id_file_field').removeAttr('required');
			$('#voter_id_file_filename_field').removeAttr('required');
			$('#declaration_form_field').removeAttr('required');
			$('#declaration_form_filename_field').removeAttr('required');
		}
		else{
			
			// Hide Passport Number and add Required attribute
			$('.passport_field').addClass('d-none');
			$('#passport_number_input').removeAttr('required');
			//$('#passport_number_input').attr('disabled', true);
			
			// Add Required attribute
			$('#aadhaar_card_number_field').attr('required', true);
			$('#adhar_card_file_front').attr('required', true);
			$('#adhar_card_file_back').attr('required', true);
			
			// Hide Kanha Voter ID tab
			$('#tab-kanha_voter_id').removeClass('d-none');
			
			/*Remove Disabled property for the fields to 
			validate Mandatory fields when this tab is active*/
			$('#birth_country_id_field').attr('required', true);
			$('#birth_state_id_field').attr('required', true);
			$('#birth_district_field').attr('required', true);
			$('#birth_town_field').attr('required', true);
			$('#already_have_kanha_voter_id_field').attr('required', true);
			/*var is_relation_required = document.getElementById("is_relation_required_input").value;
			if(is_relation_required){
				$('#relation_type_field').attr('required', true);
				$('#relative_name_field').attr('required', true);
				$('#relative_surname_field').attr('required', true);
			}
			else{
				$('#relation_type_field').attr('required', false);
				$('#relative_name_field').attr('required', false);
				$('#relative_surname_field').attr('required', false);
			}*/
		}
    },

	/**
     * Limit the size and type of a file upload. Maximum file size is 2 MB.
     *
     * @private
     */
	_onUploadPassportPhoto: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType == 'image/jpeg'){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 2) {
				Dialog.alert(null, "File is too big. File size cannot exceed 2MB.");
				// Reset fields
	        	document.getElementsByName("passport_photo_filename").value = "";
				document.getElementsByName("passport_photo").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only JPEG images.");
		}
	},
	
	/**
     * Limit the size and type of a file upload. Maximum file size is 2 MB.
     *
     * @private
     */
	_onUploadDeclarationForm: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0];
		var mimeType = file.type
		// Accepts only file with extension in jpg and jpeg
		if(mimeType == 'image/jpeg'){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 2) {
				Dialog.alert(null, "File is too big. File size cannot exceed 2MB.");
				// Reset
	        	document.getElementsByName("declaration_form_filename").value = "";
				document.getElementsByName("declaration_form").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only JPEG images.");
		}
	},
	
	/**
     * Limit the size and type of a file upload. Maximum file size is 5 MB.
     *
     * @private
     */
	_onUploadKanhaVoterIdImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0];
		var mimeType = file.type
		if(mimeType == 'image/jpeg'){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
				// Reset fields
	        	document.getElementsByName("kanha_voter_id_image_filename").value = "";
				document.getElementsByName("kanha_voter_id_image").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only JPEG images.");
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
    _adaptBirthStateAddressForm: function () {
        var $birth_country = this.$('select[name="birth_country_id"]');
        var birthCountryID = ($birth_country.val() || 0);
        this.$birthStateOptions.detach();
        var $displayedBirthState = this.$birthStateOptions.filter('[data-country_id=' + birthCountryID + ']');
        var nb = $displayedBirthState.appendTo(this.$birthState).show().length;
        //this.$state.parent().toggle(nb >= 1);
    },

	/**
     * @private
     */
    _onBirthCountryChange: function () {
        this._adaptBirthStateAddressForm();
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

 	_onDeleteVehicleLine: function (ev) {
		var $row = $(ev.currentTarget).closest("tr");
		$row.remove();
	},
    
	_onShowVehicleModal: function (ev) {
	    var $row = $(ev.currentTarget).closest("tr");
		var id = ev.target.id
	   	// var $text = $row.find("td.vehicle_number").text();
		
		// Fetch selected row's values
		var vehicle_vals = {}
		$row.each(function() {
			$(this).find('td').each(function() {
			    var name = $(this).attr('name');
				var value = $(this).html();
				if(name){
					vehicle_vals[name] = value.trim();
				}
			});
		});
		// Show modal with values
		ajax.post('/vehicle_details_form', vehicle_vals).then(function (modal) {
	 		var $modal = $(modal);
            $modal.modal({backdrop: 'static', keyboard: false});
            $modal.appendTo('body').modal();
            // Updates the values in the table
			$modal.on('click', '.save_vehicle_line', function (ev) {
				var vehicle_number = $modal.find('input[name="vehicle_number"]').val();
				var vehicle_owner = $modal.find('input[name="vehicle_owner"]').val();
				var vehicle_type = $modal.find('select[name="vehicle_type"]').val();
				// Updates the value for existing records
				if(id){
					$('#vehicle_table tr#'+id).find('.vehicle_number').text(vehicle_number)
					$('#vehicle_table tr#'+id).find('.vehicle_owner').text(vehicle_owner)
					$('#vehicle_table tr#'+id).find('.vehicle_type').text(vehicle_type)
				}
				else{
					// Add new line
					// Avoids adding empty line
					if(vehicle_number || vehicle_owner || vehicle_type)
					{
						// Insert New line before the last row
						var vehicle_table = document.getElementById('vehicle_table');
					    var index = vehicle_table.rows.length - 1;
						var newRow=document.getElementById('vehicle_table').insertRow(index);
					  	// Remove the newly added row when edit the row
						if(!$row.hasClass('empty-row')){
							$row.remove();
						}
						newRow.innerHTML = '<td class="d-none"></td><td name="vehicle_number" class="vehicle_number">'+vehicle_number+'</td><td name="vehicle_owner">'+vehicle_owner+'</td><td name="vehicle_type">'+vehicle_type+'</td><td class="text-right"><button type="button" class="btn btn-secondary fa fa-pencil mr-1 vehicle_edit_new" title="Edit" aria-label="Edit"/><button type="button" class="btn btn-secondary fa fa-trash-o vehicle_clear" title="Clear" aria-label="Clear"/></td>';
					}
				}
			 	$modal.modal('hide');	
            });
		})
	},

	_onSubmitForm: function (e) {
		var $form = $(e.currentTarget).closest('form');
        e.preventDefault(); // Prevent the default submit behavior
        // Prevent users from crazy clicking
        this.$target.find('.family_website_form_submit')
            .addClass('disabled')    // !compatibility
            .attr('disabled', 'disabled');

        var self = this;
        this.$target.find('.family_website_form_result').html(); // !compatibility
        //if (!self.check_error_fields({})) {
		var is_form_valid = Object.keys(self.check_error_fields({}))
		if (is_form_valid == 'false') {
			var missing_fields = Object.values(self.check_error_fields({}))
            self.update_status('error', _t("Please fill in the form correctly."+'\n'.concat(missing_fields.join())));
			return false;
        }
        // Prepare form inputs
        this.form_fields = $form.serializeArray();
        $.each(this.$target.find('input[type=file]'), function (outer_index, input) {
            $.each($(input).prop('files'), function (index, file) {
                // Index field name as ajax won't accept arrays of files
                // when aggregating multiple files into a single field value
                self.form_fields.push({
                    //name: input.name + '[' + outer_index + '][' + index + ']',
 					name: input.name + '[' + outer_index + '][' + index + ']',
                    value: file
                });
            });
        });

        // Serialize form inputs into a single object
        // Aggregate multiple values into arrays
        var form_values = {};
        _.each(this.form_fields, function (input) {
            if (input.name in form_values) {
                // If a value already exists for this field,
                // we are facing a x2many field, so we store
                // the values in an array.
                if (Array.isArray(form_values[input.name])) {
                    form_values[input.name].push(input.value);
                } else {
                    form_values[input.name] = [form_values[input.name], input.value];
                }
            } else {
                if (input.value !== '') {
                    form_values[input.name] = input.value;
                }
				// To save None value
				else if (input.value == '') {
                    form_values[input.name] = '';
                }

            }
        });

        // force server date format usage for existing fields
        this.$target.find('.s_website_form_field:not(.s_website_form_custom)')
        .find('.s_website_form_date, .s_website_form_datetime').each(function () {
            var date = $(this).datetimepicker('viewDate').clone().locale('en');
            var format = 'YYYY-MM-DD';
            if ($(this).hasClass('s_website_form_datetime')) {
                date = date.utc();
                format = 'YYYY-MM-DD HH:mm:ss';
            }
            form_values[$(this).find('input').attr('name')] = date.format(format);
        });

		// Prepare Vehicle Info
		var vehicle_details = {}
		var vehicle_new_lines = []
		$('#vehicle_table tbody tr:not(:last-child)').each(function() {
			var vehicle_vals = {}
			var vehicle_row_id = $(this).attr('id')
			$(this).find('td').each(function() {
			    var name = $(this).attr('name'); 
				var value = $(this).html();
				if(name){
					vehicle_vals[name] = value.trim();
				}
			});
			if(vehicle_row_id){
				vehicle_details[parseInt(vehicle_row_id)] = vehicle_vals
			}
			else{
				vehicle_new_lines.push(vehicle_vals)
			}
		});
		form_values['vehicle_details_ids'] = JSON.stringify(vehicle_details)
		form_values['vehicle_new_lines'] = JSON.stringify(vehicle_new_lines)
        
		// Post form and handle result
        ajax.post($form.attr('action') + ($form.data('force_action') || $form.data('model_name')), form_values)
        .then(function (result_data) {

            // Restore Submit button behavior
            self.$target.find('.family_website_form_submit')
                .removeAttr('disabled')
                .removeClass('disabled'); // !compatibility
            result_data = JSON.parse(result_data);
            if (!result_data.id) {
                // Failure, the server didn't return the created record ID
                self.update_status('error', result_data.error_message ? result_data.error_message : false);
                if (result_data.error_fields) {
                    // If the server return a list of bad fields, show these fields for users
                    self.check_error_fields(result_data.error_fields);
                }
            } else {
                // Success, redirect or update status
                let successMode = $form[0].dataset.successMode;
                let successPage = $form[0].dataset.successPage;
                if (!successMode) {
                    successPage = $form.attr('data-success_page'); // Compatibility
                    successMode = successPage ? 'redirect' : 'nothing';
                }
                switch (successMode) {
                    case 'redirect':
                        if (successPage.charAt(0) === "#") {
                            dom.scrollTo($(successPage)[0], {
                                duration: 500,
                                extraOffset: 0,
                            });
                        } else {
                            $(window.location).attr('href', successPage);
                        }
                        break;
                    case 'message':
                        self.$target[0].classList.add('d-none');
                        self.$target[0].parentElement.querySelector('.s_website_form_end_message').classList.remove('d-none');
                        break;
                    default:
                        self.update_status('success');
                        break;
                }
            }
        })
        .guardedCatch(function () {
            self.update_status('error');
        });
    },

	check_error_fields: function (error_fields) {
        var self = this;
        var form_valid = true;
		var missing_fields = []
		var missing_field_vals = {}
        // Loop on all fields
        this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { // !compatibility
            var $field = $(field);
            var field_name = $field.find('.col-form-label').attr('for');

            // Validate inputs for this field
            var inputs = $field.find('.s_website_form_input, .o_website_form_input').not('#editable_select'); // !compatibility
            var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
                // Special check for multiple required checkbox for same
                // field as it seems checkValidity forces every required
                // checkbox to be checked, instead of looking at other
                // checkboxes with the same name and only requiring one
                // of them to be checked.
                if (input.required && input.type === 'checkbox') {
                    // Considering we are currently processing a single
                    // field, we can assume that all checkboxes in the
                    // inputs variable have the same name
                    var checkboxes = _.filter(inputs, function (input) {
                        return input.required && input.type === 'checkbox';
                    });
                    return !_.any(checkboxes, checkbox => checkbox.checked);

                // Special cases for dates and datetimes
                } else if ($(input).hasClass('s_website_form_date') || $(input).hasClass('o_website_form_date')) { // !compatibility
                    if (!self.is_datetime_valid(input.value, 'date')) {
                        return true;
                    }
                } else if ($(input).hasClass('s_website_form_datetime') || $(input).hasClass('o_website_form_datetime')) { // !compatibility
                    if (!self.is_datetime_valid(input.value, 'datetime')) {
                        return true;
                    }
                }
                return !input.checkValidity();
            });

            // Update field color if invalid or erroneous
            $field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
            
			if (invalid_inputs.length || error_fields[field_name]) {
				// Stores Field's' Lable name for required fields used to display in the warning message
				if(field_name != undefined){
					missing_fields.push(field_name)
				}
                $field.addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                if (_.isString(error_fields[field_name])) {
                    $field.popover({content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top'});
                    // update error message and show it.
                    $field.data("bs.popover").config.content = error_fields[field_name];
                    $field.popover('show');
                }
                form_valid = false;
            }
        });
        //return form_valid;
		missing_field_vals[form_valid] = missing_fields
		return missing_field_vals;
    },

    is_datetime_valid: function (value, type_of_date) {
        if (value === "") {
            return true;
        } else {
            try {
                this.parse_date(value, type_of_date);
                return true;
            } catch (e) {
                return false;
            }
        }
    },

    // This is a stripped down version of format.js parse_value function
    parse_date: function (value, type_of_date, value_if_empty) {
        var date_pattern = time.getLangDateFormat(),
            time_pattern = time.getLangTimeFormat();
        var date_pattern_wo_zero = date_pattern.replace('MM', 'M').replace('DD', 'D'),
            time_pattern_wo_zero = time_pattern.replace('HH', 'H').replace('mm', 'm').replace('ss', 's');
        switch (type_of_date) {
            case 'datetime':
                var datetime = moment(value, [date_pattern + ' ' + time_pattern, date_pattern_wo_zero + ' ' + time_pattern_wo_zero], true);
                if (datetime.isValid()) {
                    return time.datetime_to_str(datetime.toDate());
                }
                throw new Error(_.str.sprintf(_t("'%s' is not a correct datetime"), value));
            case 'date':
                var date = moment(value, [date_pattern, date_pattern_wo_zero], true);
                if (date.isValid()) {
                    return time.date_to_str(date.toDate());
                }
                throw new Error(_.str.sprintf(_t("'%s' is not a correct date"), value));
        }
        return value;
    },

    update_status: function (status, message) {
        if (status !== 'success') { // Restore submit button behavior if result is an error
            this.$target.find('.family_website_form_submit')
                .removeAttr('disabled')
                .removeClass('disabled'); // !compatibility
        }
		if ((status === 'error') || (status !== 'success')) {
			var $result = this.$('.family_website_form_result');
			this.$('#form_result_error').removeClass('d-none')

        }
		else{
			var $result = this.$('.family_website_form_result');
			this.$('#form_result_success').removeClass('d-none')
		}
		if (status === 'error' && !message) {
            message = _t("An error has occured, the form has not been sent.");
        }
        // Note: we still need to wait that the widget is properly started
        // before any qweb rendering which depends on xmlDependencies
        // because the event handlers are binded before the call to
        // willStart for public widgets...
        $result.html(
           message
        );
    },
});
});
