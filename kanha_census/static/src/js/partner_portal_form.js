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
		'change select[name="relation_type"]': '_onChangeRelationType',
		'change select[name="change_voter_id_address"]': '_onChangeVoterAddressToKanha',
		'change select[name="citizenship"]': '_onCitizenshipChange',
		//'change select[name="application_type"]': '_onChangeVoterApplicationType',
		'change select[name="already_have_kanha_voter_id"]': '_onChangeAlreadyHaveKanhaVoterID',
		'change select[name="need_new_kanha_voter_id"]': '_onChangeNeedNewKanhaVoterID',
		// Adhar File Front upload
		'click .adhar_file_edit': '_onBrowseFile',
		'change .adhar_file_upload': '_onUploadAdharFrontImage',
		'click .adhar_file_browse': '_onBrowseFile',
		'click .adhar_file_clear': '_onClearFile',
		// Adhar File Back upload
		'click .adhar_file_back_side_edit': '_onBrowseFile',
		'change .adhar_file_back_side_upload': '_onUploadAdharBackImage',
		'click .adhar_file_back_side_browse': '_onBrowseFile',
		'click .adhar_file_back_side_clear': '_onClearFile',
		// Age proof File upload
		'click .age_proof_edit': '_onBrowseFile',
		'change .age_proof_upload': '_onUploadAgeProof',
		'click .age_proof_browse': '_onBrowseFile',
		'click .age_proof_clear': '_onClearFile',
		// Address File upload
		'click .address_proof_edit': '_onBrowseFile',
		'change .address_proof_upload': '_onUploadAddressProof',
		'click .address_proof_browse': '_onBrowseFile',
		'click .address_proof_clear': '_onClearFile',
		// Indian Visa upload
		'click .indian_visa_edit': '_onBrowseFile',
		'change .indian_visa_upload': '_onUploadIndianVisa',
		'click .indian_visa_browse': '_onBrowseFile',
		'click .indian_visa_clear': '_onClearFile',
		// Passport Photot upload
		'click .passport_photo_edit': '_onBrowseFile',
		'change .passport_photo_upload': '_onUploadPassportPhoto',
		'click .passport_photo_browse': '_onBrowseFile',
		'click .passport_photo_clear': '_onClearFile',
		// Passport Front image upload
		'click .passport_front_image_edit': '_onBrowseFile',
		'change .passport_front_image_upload': '_onUploadPassportFrontImage',
		'click .passport_front_image_browse': '_onBrowseFile',
		'click .passport_front_image_clear': '_onClearFile',
		// Passport Back image upload
		'click .passport_back_image_edit': '_onBrowseFile',
		'change .passport_back_image_upload': '_onUploadPassportBackImage',
		'click .passport_back_image_browse': '_onBrowseFile',
		'click .passport_back_image_clear': '_onClearFile',
		// Kanha voter ID image upload
		'click .kanha_voter_id_image_browse': '_onBrowseFile',
		'change .kanha_voter_id_image_upload': '_onUploadKanhaVoterIdImage',
		'click .kanha_voter_id_image_edit': '_onBrowseFile',
		'click .kanha_voter_id_image_clear': '_onClearFile',
		// Kanha Voter ID Back Image upload
		'click .kanha_voter_id_back_image_browse': '_onBrowseFile',
		'change .kanha_voter_id_back_image_upload': '_onUploadKanhaVoterIdBackImage',
		'click .kanha_voter_id_back_image_edit': '_onBrowseFile',
		'click .kanha_voter_id_back_image_clear': '_onClearFile',
		// voter ID File upload
		//'click .voter_id_file_browse': '_onBrowseFile',
		//'change .voter_id_file_upload': '_onFileUploadChange',
		//'click .voter_id_file_edit': '_onBrowseFile',
		//'click .voter_id_file_clear': '_onClearFile',
		// Declaration Form upload
		//'click .declaration_form_edit': '_onBrowseFile',
		//'change .declaration_form_upload': '_onUploadDeclarationForm',
		//'click .declaration_form_browse': '_onBrowseFile',
		//'click .declaration_form_clear': '_onClearFile',
		// Country selection
		'change select[name="birth_country_id"]': '_onBirthCountryChange',
		'change select[name="country_id"]': '_onCountryChange',
		// Kanha Location Selection
		'change select[name="kanha_location_id"]': '_onKanhaLocationChange',
		'change select[name="work_profile_id"]': '_onWorkProfileChange',

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
		'keypress #passport_front_image_file': '_onRestrictInput',
		'keydown #passport_front_image_file': '_onRestrictInput',
		'keypress #passport_back_image_file': '_onRestrictInput',
		'keydown #passport_back_image_file': '_onRestrictInput',
		'keypress #indian_visa_file': '_onRestrictInput',
		'keydown #indian_visa_file': '_onRestrictInput',
		'keypress #age_proof_file': '_onRestrictInput',
		'keydown #age_proof_file': '_onRestrictInput',
		'keypress #address_proof_file': '_onRestrictInput',
		'keydown #address_proof_file': '_onRestrictInput',
		'keypress #kanha_voter_id_image_filename_field': '_onRestrictInput',
		'keydown #kanha_voter_id_image_filename_field': '_onRestrictInput',
		'keypress #kanha_voter_id_back_image_filename_field': '_onRestrictInput',
		'keydown #kanha_voter_id_back_image_filename_field': '_onRestrictInput',
		// 'keypress #voter_id_file_filename_field': '_onRestrictInput',
		// 'keydown #voter_id_file_filename_field': '_onRestrictInput',
		//'keypress #declaration_form_filename_field': '_onRestrictInput',
		//'keydown #declaration_form_filename_field': '_onRestrictInput',
		// Form submit
		'click .family_website_form_submit': '_onSubmitForm',
		// Form Save
		'click .family_website_form_save': '_onClickSave',
		//'click .family_website_form_save': '_onSubmitForm',
		// Adhaar card input auto space
		'keypress #aadhaar_card_number_field': '_insertCardNumberBlankSpace',
		'change #aadhaar_card_number_field': '_insertCardNumberBlankSpace',
		// 'keypress #relative_aadhaar_card_number_field': '_insertCardNumberBlankSpace',
		// 'change #relative_aadhaar_card_number_field': '_insertCardNumberBlankSpace',
		'keypress #pan_card_number_id': '_restrictSpecialCharacter',
		'keydown #pan_card_number_id': '_restrictSpecialCharacter',
		'keypress #mobile_number_id': '_restrictSpecialCharacter',
		'keydown #mobile_number_id': '_restrictSpecialCharacter',
		'click .partner_clear': '_onClickDeletePartner',

		
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
		this.$kanhaHouseNumber = this.$('select[name="kanha_house_number_id"]');
        this.$kanhaHouseNumberOptions = this.$kanhaHouseNumber.filter(':enabled').find('option:not(:first)');
		this._adaptKanhaHouseNumberStateAddressForm();
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
	
	_restrictSpecialCharacter(e) {  
	    var k;  
	    document.all ? k = e.keyCode : k = e.which;  
	    return ((k > 64 && k < 91) || (k > 96 && k < 123) || k == 9 || k == 8 || k == 32 || (k >= 48 && k <= 57));  
	}, 
	
	/**
     * Insert blank space after every 4 digits
     *
     * @private
     */
	_insertCardNumberBlankSpace: function (e) {
		var restrictSpecialChar = this._restrictSpecialCharacter(e)
  		e.target.value = e.target.value.replace(/[^\dA-Z]/g, '').replace(/(.{4})/g, '$1 ').trim();
		return restrictSpecialChar;

	},


	/* deletes a record */
	_onClickDeletePartner: function (e) {
		var def = new Promise(function (resolve, reject) {
            var message = _t("Are you sure you want to delete this record?");
            var dialog = Dialog.confirm(self, message, {
                title: _t("Confirmation"),
                confirm_callback: function() {
					var self = this;
					var deleted_partner_ids = []
					var partner_id = $(e.target).attr('id')
					deleted_partner_ids.push(partner_id)
					var form_values = {};
					form_values['deleted_partner_ids'] = deleted_partner_ids
					
					// Post form and handle result
					ajax.post('/delete_family_members', form_values)
					.then(function (result) {
						var result_span = self.$('.family_delete_result');   
						self.$('#delete_result').removeClass('d-none')
						if(result == "deleted") {
							//result_span.html("Record has been deleted successfully");
							Dialog.alert(self, _t("Record has been deleted successfully."), {
								confirm_callback: function() {
									$(window.location).attr('href', "/family/");
								},
							});	
						}   
						else if(result == "current_user") {		        
							// result_span.html("Please contact Administrator to delete the record");
							Dialog.alert(null, "Please contact Administrator to delete the record.");
						}
						else if(result == "cannot_delete") {		        
							// result_span.html("Please contact Administrator to delete the record");
							Dialog.alert(null, "You can delete only Rejected and Not Yet Submitted records.");
						}
						
						// $("html, body").animate({ scrollTop: 0 }, "slow");
					})
					.guardedCatch(function () {
						self.update_status('error');
					});
				},
                cancel_callback: reject,
            });
            dialog.on('closed', self, reject);
        });
	},

	_onChangeRelationType: function (ev) {
		// document.getElementById("relation_type_field").value = "";
        // $(ev.currentTarget).closest('form').find('select[name="relation_type"]').trigger('change');
	
		var relation_type = this.$('select[name="relation_type"]');
		if(relation_type.val() == 'Other'){
			$('.relation_other_class').removeClass('d-none');
		}
		else{
			$('.relation_other_class').addClass('d-none');
		}
	},



	_onWorkProfileChange: function (ev) {
	
		var work_profile = this.$('select[name="work_profile_id"]');
		var selected_work_profile = ev.target.selectedOptions[0].getAttribute('name')
		if(selected_work_profile == 'Employee'){
			$('.department').removeClass('d-none');
			$('.employee_id').removeClass('d-none');
		}
		else{
			document.getElementById("department_id").value = "";
			document.getElementById("employee_id_id").value = "";

			$('.department').addClass('d-none');
			$('.employee_id').addClass('d-none');
		}
	},


	/**
     * Show/Hide Voter ID details based on selected value of Change Voter ID address
     *
     * @private
     */
    _onChangeVoterAddressToKanha: function (ev) {
		document.getElementById("application_type_field").value = "";
        $(ev.currentTarget).closest('form').find('select[name="application_type"]').trigger('change');
	
		var voter_is_there = this.$('select[id="already_have_kanha_voter_id_field"]');
		var voter_address_change = this.$('select[name="change_voter_id_address"]');
		if(voter_address_change.val() == 'Yes'){
			$('.voter_id_tab').removeClass('d-none');
			
			/*Set Required attribute for the fields to 
			validate Mandatory fields only when this tab is active*/
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
				$('#application_type_field').change()
			}
			
			/*$('.kanha_voter_id_number').addClass('d-none');
			$('#kanha_voter_id_number_field').removeAttr('required');*/
		
		}
		else{
			
			/*$('.kanha_voter_id_number').removeClass('d-none');
			$('#kanha_voter_id_number_field').attr('required', true);*/
			var is_voter_tab_active = $('a.voter_id_tab').hasClass('active');
			$('.voter_id_tab').addClass('d-none');
			
			/*Remove Required attribute when this tab is hide*/
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
			
			/*Navigate user to Kanha Address tab if Existing Voter ID tab hides.
			 when user on the Existing Voter ID tab*/
			if(is_voter_tab_active)
			{
				$('a.active').removeClass("active");
				$('div.active').removeClass("active");
				$('#tab-kanha').addClass('active');
				$('#pane-kanha').addClass('active');
				$('#pane-kanha').addClass('show');

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
			
			$('.kanha_voter_id_back_image').removeClass('d-none');
			$('#kanha_voter_id_back_image_field').attr('required', true);
			
			$('.change_voter_id_address').removeClass('d-none');
			
		}
		else if(already_have_kanha_voter_id.val() == 'No'){
			
			$('#change_voter_id_address_field').val("");
			$('#change_voter_id_address_field').change();

			// Hide Kanha Voter ID number and Kanha Voter ID image fields and remove required attribute			
			$('.kanha_voter_id_number').addClass('d-none');
			$('#kanha_voter_id_number_field').removeAttr('required');
			//document.getElementById("kanha_voter_id_number_field").value = "";
			
			$('.kanha_voter_id_image').addClass('d-none');
			$('#kanha_voter_id_image_field').removeAttr('required');
			
			$('.kanha_voter_id_back_image').addClass('d-none');
			$('#kanha_voter_id_back_image_field').removeAttr('required');
			
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
			
			$('.kanha_voter_id_back_image').addClass('d-none');
			$('#kanha_voter_id_back_image_field').removeAttr('required');
			
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
			$('#application_type_field').change()
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
    //_onChangeVoterApplicationType: function () {
	//	var application_type = this.$('select[name="application_type"]');
	//	if(application_type.val() == 'New Application'){
			
			// Show Declaration Form field
			//$('.declaration_form').removeClass('d-none');
			//$('#declaration_form_field').attr('required', true);
			
			// Hide Existing Voter ID number and Voter ID file
			// $('.existing_voter_id_number').addClass('d-none');
			// $('#existing_voter_id_number_field').removeAttr('required');
			//document.getElementById("existing_voter_id_number_field").value = "";
			
			// $('.voter_id_file').addClass('d-none');
			// $('#voter_id_file_field').removeAttr('required');
			//document.getElementById("voter_id_file_field").value = "";
			//document.getElementById("voter_id_file_filename_field").value = "";
			
	//	}
	//	else if(application_type.val() == 'Transfer Application'){
			// Hide Declaration Form field
			//$('.declaration_form').addClass('d-none');
			//$('#declaration_form_field').removeAttr('required');
			//document.getElementById("declaration_form_field").value = "";
			//document.getElementById("declaration_form_filename_field").value = "";
			
			// Show Existing Voter ID number and Voter ID file
			// $('.existing_voter_id_number').removeClass('d-none');
			// $('#existing_voter_id_number_field').attr('required', true);
			
			// $('.voter_id_file').removeClass('d-none');
			// $('#voter_id_file_field').attr('required', true);
			
	//	}
	//	else{
			
			// // Hide Existing Voter ID number and Voter ID file
			// $('.existing_voter_id_number').addClass('d-none');
			// $('#existing_voter_id_number_field').removeAttr('required');
			// //document.getElementById("existing_voter_id_number_field").value = "";

			// $('.voter_id_file').addClass('d-none');
			// $('#voter_id_file_field').removeAttr('required');
			//document.getElementById("voter_id_file_field").value = "";
			//document.getElementById("voter_id_file_filename_field").value = "";
			
			// Hide Declaration Form field
			//$('.declaration_form').addClass('d-none');
			//$('#declaration_form_field').removeAttr('required');
			//document.getElementById("declaration_form_field").value = "";
			//document.getElementById("declaration_form_filename_field").value = "";
	//	}
    //},

	/**
     * Show Passport Number and Hide Kanha Voter ID tab if selected Citizenship is Overseas
     *
     * @private
     */
	_onCitizenshipChange: function () {
		var citizenship = this.$('select[name="citizenship"]');
		if(citizenship.val() == 'Overseas'){
			$('#change_voter_id_address_field').val("");
			$('#change_voter_id_address_field').change();
			$('#already_have_kanha_voter_id_field').val("")
			$('#already_have_kanha_voter_id_field').change()
			// Show Passport Number, Passport ID image and Indian Visa image and add Required attribute
			$('.passport_field').removeClass('d-none');
			$('#passport_number_input').attr('required', true);
			$('.passport_front_image_div').removeClass('d-none');
			$('.passport_back_image_div').removeClass('d-none');
			$('#passport_front_image_file').attr('required', true);
			$('#passport_back_image_file').attr('required', true);
			$('.indian_visa_div').removeClass('d-none');
			$('#indian_visa_file').attr('required', true);

			// Remove Mandatory validation
			$('#aadhaar_card_number_field').removeAttr('required');
			$("label[for='Aadhaar Card Number']").next(".s_website_form_mark").addClass('d-none')
			$("label[for='Aadhar Card Front']").next(".s_website_form_mark").addClass('d-none')
			$("label[for='Aadhar Card Back']").next(".s_website_form_mark").addClass('d-none')
			$('#adhar_card_file_front').removeAttr('required');
			$("#adhar_card_file_front").next(".s_website_form_mark").addClass('d-none')
			$('#adhar_card_file_back').removeAttr('required');
			$("#adhar_card_file_back").next(".s_website_form_mark").addClass('d-none')
			
			/*Navigate user to Kanha Address tab if Existing Voter ID tab hides.
			 when user on the Existing Voter ID tab*/
			var is_kanha_voter_tab_active = $('a#tab-kanha_voter_id').hasClass('active');
			// Hide Kanha Voter ID tab
			$('#tab-kanha_voter_id').addClass('d-none');
			$('#pane-kanha_voter_id').addClass('d-none');
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
			$('#kanha_voter_id_back_image_field').removeAttr('required');
			$('#kanha_voter_id_back_image_filename_field').removeAttr('required');
			$('#need_new_kanha_voter_id_field').removeAttr('required');
			$('#application_type_field').removeAttr('required');
			$('#existing_voter_id_number_field').removeAttr('required');
			$('#voter_id_file_field').removeAttr('required');
			$('#voter_id_file_filename_field').removeAttr('required');
			//$('#declaration_form_field').removeAttr('required');
			//$('#declaration_form_filename_field').removeAttr('required');
		}
		else{
			
			// Hide Passport Number and add Required attribute
			$('.passport_field').addClass('d-none');
			$('#passport_number_input').removeAttr('required');
			$('.passport_front_image_div').addClass('d-none');
			$('.passport_back_image_div').addClass('d-none');
			$('#passport_front_image_file').removeAttr('required');
			$('#passport_back_image_file').removeAttr('required');
			$('.indian_visa_div').addClass('d-none');
			$('#indian_visa_file').removeAttr('required');
			//$('#passport_number_input').attr('disabled', true);
			
			// Add Required attribute
			$("label[for='Aadhaar Card Number']").next(".s_website_form_mark").removeClass('d-none')
			$("label[for='Aadhar Card Front']").next(".s_website_form_mark").removeClass('d-none')
			$("label[for='Aadhar Card Back']").next(".s_website_form_mark").removeClass('d-none')
			$('#aadhaar_card_number_field').attr('required', true);
			$('#adhar_card_file_front').attr('required', true);
			$('#adhar_card_file_back').attr('required', true);
			
			// Hide Kanha Voter ID tab
			$('#tab-kanha_voter_id').removeClass('d-none');
			$('#pane-kanha_voter_id').removeClass('d-none');
			
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
	 _onUploadPassportFrontImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
				// Reset fields
	        	document.getElementsByName("passport_front_image_filename").value = "";
				document.getElementsByName("passport_front_iamge").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only image files.");
		}
	},

	/**
     * Limit the size and type of a file upload. Maximum file size is 2 MB.
     *
     * @private
     */
	 _onUploadPassportBackImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
				// Reset fields
	        	document.getElementsByName("passport_back_image_filename").value = "";
				document.getElementsByName("passport_back_iamge").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only image files.");
		}
	},

	/**
     * Limit the size and type of a file upload. Maximum file size is 2 MB.
     *
     * @private
     */
	 _onUploadIndianVisa: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
				// Reset fields
	        	document.getElementsByName("indian_visa_filename").value = "";
				document.getElementsByName("indian_visa").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only image files.");
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
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
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
			Dialog.alert(null, "Accepts only image files.");
		}
	},
	
	/**
     * Limit the size and type of a file upload. Maximum file size is 2 MB.
     *
     * @private
     */
	// _onUploadDeclarationForm: function (ev) {
	// 	var files = ev.target.files;
	// 	if (!files.length) {
    //         return;
    //     }
	// 	var file = files[0];
	// 	var mimeType = file.type
	// 	// Accepts only file with extension in jpg and jpeg
	// 	if(mimeType.indexOf("image/") == 0){
	// 	  	var fileSize = file.size / 1024 / 1024; // in MiB
	//   		if (fileSize > 5) {
	// 			Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
	// 			// Reset
	//         	document.getElementsByName("declaration_form_filename").value = "";
	// 			document.getElementsByName("declaration_form").value = "";
	// 		}
	// 		else{
	// 			var file_name = ev.target.files[0].name
	// 			var $form = $(ev.currentTarget).closest('form');
	// 			var filename_input = $(ev.target).attr('filename_input')
	// 			$form.find('.'+filename_input).val(file_name);
	// 		}
	// 	}
	// 	else{
	// 		Dialog.alert(null, "Accepts only image files.");
	// 	}
	// },
	
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
		if(mimeType.indexOf("image/") == 0){
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
			Dialog.alert(null, "Accepts only image files.");
		}
	},
	
	/**
     * Limit the size and type of a file upload. Maximum file size is 5 MB.
     *
     * @private
     */
	_onUploadKanhaVoterIdBackImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0];
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
				// Reset fields
	        	document.getElementsByName("kanha_voter_id_back_image_filename").value = "";
				document.getElementsByName("kanha_voter_id_back_image").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only image files.");
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

	_onUploadAgeProof: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
				// Reset fields
	        	document.getElementsByName("age_proof_filename").value = "";
				document.getElementsByName("age_proof").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only image files.");
		}
	},

	_onUploadAddressProof: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
				// Reset fields
	        	document.getElementsByName("address_proof_filename").value = "";
				document.getElementsByName("address_proof").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only image files.");
		}
	},

	_onUploadAdharFrontImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
				// Reset fields
	        	document.getElementsByName("adhar_card_filename").value = "";
				document.getElementsByName("adhar_front").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only image files.");
		}
	},

	_onUploadAdharBackImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024; // in MiB
	  		if (fileSize > 5) {
				Dialog.alert(null, "File is too big. File size cannot exceed 5MB.");
				// Reset fields
	        	document.getElementsByName("adhar_card_back_side_filename").value = "";
				document.getElementsByName("adhar_back").value = "";
			}
			else{
				var file_name = ev.target.files[0].name
				var $form = $(ev.currentTarget).closest('form');
				var filename_input = $(ev.target).attr('filename_input')
				$form.find('.'+filename_input).val(file_name);
			}
		}
		else{
			Dialog.alert(null, "Accepts only image files.");
		}
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
		// If country doesnt have state remove required for state
		// var brith_state = document.getElementById("birth_state_id_field");
		// if(typeof brith_state !== 'undefined' && brith_state !== null) {
		// 	var birth_state_options = brith_state.options;
		// 	if(birth_state_options.length > 1){
		// 		$('#birth_state_id_field').attr('required', true);
		// 		$('#birth_district_field').attr('required', true);
				
		// 	}
		// 	else{
		// 		$('#birth_state_id_field').attr('required', false);
		// 		$('#birth_district_field').attr('required', false);
		// 	}
		// }

		var birth_country = document.getElementById("birth_country_id_field");
		if(typeof birth_country !== 'undefined' && birth_country !== null) {
			var selected_country = birth_country.options[birth_country.selectedIndex].text;
			if(selected_country.trim() == 'India'){
				$('#birth_state_id_field').attr('required', true);
				$('#birth_state_textfield_id').attr('required', false);

				$('.birth_state_dropdown_field_div').removeClass('d-none');
				$('.birth_state_textfield_div').addClass('d-none');
			}
			else{
				$('#birth_state_id_field').attr('required', false);
				$('#birth_state_textfield_id').attr('required', true);

				$('.birth_state_dropdown_field_div').addClass('d-none');
				$('.birth_state_textfield_div').removeClass('d-none');
			}
		}
    },

	/**
     * @private
     */
    _onKanhaLocationChange: function () {
        this._adaptKanhaHouseNumberStateAddressForm();
    },

	/**
     * @private
     */
	 _adaptKanhaHouseNumberStateAddressForm: function () {
		var $kanha_location = this.$('select[name="kanha_location_id"]');
        var KanhaLocationID = ($kanha_location.val() || 0);
        this.$kanhaHouseNumberOptions.detach();
        var $displayedKanhaHouseNumber = this.$kanhaHouseNumberOptions.filter('[data-kanha_location_id=' + KanhaLocationID + ']');
        var nb = $displayedKanhaHouseNumber.appendTo(this.$kanhaHouseNumber).show().length;
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
				$(".save_vehicle_line").attr('disabled',true)
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

	/* saves a record */
	_onSaveForm: function (e, is_submit) {
		//Show loading
		$("#loading").removeClass('hide');
		var $form = $(e.currentTarget).closest('form');
		var self = this;
		
		/*// Clear form submission status if any
		this.$('#form_result_error').addClass('d-none')
		
		// Update field color if invalid or erroneous
		this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { 
			var $field = $(field);
        	$field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
 		});*/
	
	
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
		form_values['is_submit'] = is_submit;


		var birth_country = document.getElementById("birth_country_id_field");
		if(typeof birth_country !== 'undefined' && birth_country !== null) {
			var selected_country = birth_country.options[birth_country.selectedIndex].text;
			if(selected_country.trim() == 'India'){
				form_values['birth_state_textfield'] = '';
			}
		}
        
		// Post form and handle result
        ajax.post($form.attr('action') + ($form.data('force_action') || $form.data('model_name')), form_values)
        .then(function (result_data) {
			// Hide Loading
	    	$("#loading").addClass('hide');
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
                    //self.check_error_fields(result_data.error_fields);
					self.check_error_fields_save(Object.keys(result_data.error_fields))
					self.$target.find('.family_website_form_save').removeClass('disabled').attr('enabled', 'enabled');
					//window.scrollTo(0,0);
					$("html, body").animate({ scrollTop: 0 }, "slow");

					
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
						    if( is_submit == true) {
								$(window.location).attr('href', successPage);
							}   
						    else {
								$(window.location).attr('href', "/family/");
						   		//let saveSuccessPage = $form[0].dataset.saveSuccessPage;
								//$(window.location).attr('href', saveSuccessPage);
								//location.reload()
								
								// Prevent users from crazy clicking
						        /*self.$target.find('.family_website_form_save')
						            .removeClass('disabled')    // !compatibility
						            .attr('disabled', false);
								self.$('#form_result_success').removeClass('d-none')
								setTimeout(function(){
									$(window.location).attr('href', "/website_form_family/"+result_data.id+"/res.partner");
            					}, 1000);*/
								//self.update_status('success', _t("The form has been saved successfully."));
							}
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
	
	
	_validateForm: function (e) {
        e.preventDefault(); // Prevent the default submit behavior
        // Prevent users from crazy clicking
        /*this.$target.find('.family_website_form_submit')
            .addClass('disabled')    // !compatibility
            .attr('disabled', 'disabled');*/
		
		// Clear form submission status if any
		// this.$('#form_result_success').addClass('d-none')

        var self = this;
        this.$target.find('.family_website_form_result').html(); // !compatibility
        //if (!self.check_error_fields({})) {
		var is_form_valid = Object.keys(self.check_error_fields({}))
		if (is_form_valid == 'false') {
			var missing_fields = Object.values(self.check_error_fields({}))
            self.update_status('error', _t("Please fill in the form correctly."+'\n'.concat(missing_fields.join())));
			return false;
        }
		return true;
    },

	_clearFormStatus: function (e) {
		// Clear form submission status if any
		this.$('#form_result_error').addClass('d-none');
		
		// Update field color if invalid or erroneous
		this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { 
			var $field = $(field);
        	$field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
 		});
	},
	
	// Saves the form values. If form submit is False then ignore the form validation
	_onClickSave: function (e, is_submit=false) {

		this._clearFormStatus(e);
		var citizenship = $('.citizenship').val();
		var aadhaar_card_number = $('#aadhaar_card_number_field').val();
		var passport_number = $('#passport_number_input').val();
		var name_input = $('#name_input').val();
		if(!name_input){
			$('#name_input').addClass('is-invalid');
			this.update_status('error', _t("Name is Mandatory to Save Record!"));
			$("html, body").animate({ scrollTop: 0 }, "slow");
			return false;
		}
		if(citizenship == 'Indian' && !aadhaar_card_number){
			$('#aadhaar_card_number_field').addClass('is-invalid');
			this.update_status('error', _t("Aadhaar Card Number is Mandatory to Save/Submit Record!"));
			$("html, body").animate({ scrollTop: 0 }, "slow");
			return false;
		}
		if(citizenship == 'Overseas' && !passport_number){
			$('#passport_number_input').addClass('is-invalid');
			this.update_status('error', _t("Passport Number is Mandatory to Save/Submit Record!"));
			$("html, body").animate({ scrollTop: 0 }, "slow");
			return false;
		}
		this._onSaveForm(e, is_submit);
	},
	
	_onSubmitForm: function (e) {
		//this._clearFormStatus(e)
		var res = this._validateForm(e)
		if(res){
			this._onSaveForm(e, true);
		}
		else{
			$("html, body").animate({ scrollTop: 0 }, "slow");
			return false;
		}
    },

	check_error_fields_save: function (error_fields_keys) {
		for (let i = 0; i < error_fields_keys.length; i++) {
			$("input[name='"+error_fields_keys[i]+"']").addClass('is-invalid');
		} 
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
				
				//$("html, body").animate({ scrollTop: 0 }, "slow");
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
			if(message){
				this.$('#form_result_success').removeClass('d-none')
			}
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
