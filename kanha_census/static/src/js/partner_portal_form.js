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
		'change select[name="already_have_kanha_voter_id"]': '_onChangeAlreadyHaveKanhaVoterID',
		'change select[name="need_new_kanha_voter_id"]': '_onChangeNeedNewKanhaVoterID',
		'click .adhar_file_edit': '_onBrowseFile',
		'change .adhar_file_upload': '_onUploadAdharFrontImage',
		'click .adhar_file_browse': '_onBrowseFile',
		'click .adhar_file_clear': '_onClearFile',
		'click .adhar_file_back_side_edit': '_onBrowseFile',
		'change .adhar_file_back_side_upload': '_onUploadAdharBackImage',
		'click .adhar_file_back_side_browse': '_onBrowseFile',
		'click .adhar_file_back_side_clear': '_onClearFile',
		'click .age_proof_edit': '_onBrowseFile',
		'change .age_proof_upload': '_onUploadAgeProof',
		'click .age_proof_browse': '_onBrowseFile',
		'click .age_proof_clear': '_onClearFile',
		'click .address_proof_edit': '_onBrowseFile',
		'change .address_proof_upload': '_onUploadAddressProof',
		'click .address_proof_browse': '_onBrowseFile',
		'click .address_proof_clear': '_onClearFile',
		'click .indian_visa_edit': '_onBrowseFile',
		'change .indian_visa_upload': '_onUploadIndianVisa',
		'click .indian_visa_browse': '_onBrowseFile',
		'click .indian_visa_clear': '_onClearFile',
		'click .passport_photo_edit': '_onBrowseFile',
		'change .passport_photo_upload': '_onUploadPassportPhoto',
		'click .passport_photo_browse': '_onBrowseFile',
		'click .passport_photo_clear': '_onClearFile',
		'click .passport_front_image_edit': '_onBrowseFile',
		'change .passport_front_image_upload': '_onUploadPassportFrontImage',
		'click .passport_front_image_browse': '_onBrowseFile',
		'click .passport_front_image_clear': '_onClearFile',
		'click .passport_back_image_edit': '_onBrowseFile',
		'change .passport_back_image_upload': '_onUploadPassportBackImage',
		'click .passport_back_image_browse': '_onBrowseFile',
		'click .passport_back_image_clear': '_onClearFile',
		'click .kanha_voter_id_image_browse': '_onBrowseFile',
		'change .kanha_voter_id_image_upload': '_onUploadKanhaVoterIdImage',
		'click .kanha_voter_id_image_edit': '_onBrowseFile',
		'click .kanha_voter_id_image_clear': '_onClearFile',
		'click .kanha_voter_id_back_image_browse': '_onBrowseFile',
		'change .kanha_voter_id_back_image_upload': '_onUploadKanhaVoterIdBackImage',
		'click .kanha_voter_id_back_image_edit': '_onBrowseFile',
		'click .kanha_voter_id_back_image_clear': '_onClearFile',
		'change select[name="birth_country_id"]': '_onBirthCountryChange',
		'change select[name="country_id"]': '_onCountryChange',
		'change select[name="kanha_location_id"]': '_onKanhaLocationChange',
		'change select[name="work_profile_id"]': '_onWorkProfileChange',
		'click .vehicle_add_new': '_onShowVehicleModal',
		'click .vehicle_edit_new': '_onShowVehicleModal',
		'click .vehicle_edit_exist': '_onShowVehicleModal',
		'click .save_vehicle_line': '_onSaveVehicle',
		'click .vehicle_clear': '_onDeleteVehicleLine',
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
		'click .family_website_form_submit': '_onSubmitForm',
		'click .family_website_form_save': '_onClickSave',
		'keypress #aadhaar_card_number_field': '_insertCardNumberBlankSpace',
		'change #aadhaar_card_number_field': '_insertCardNumberBlankSpace',
		'keypress #pan_card_number_id': '_restrictSpecialCharacter',
		'keydown #pan_card_number_id': '_restrictSpecialCharacter',
		'keypress #mobile_number_id': '_restrictSpecialCharacter',
		'keydown #mobile_number_id': '_restrictSpecialCharacter',
		'click .partner_clear': '_onClickDeletePartner',
		'change select[name="do_you_need_voter_id_in_kanha"]': '_onVoterIdChange',
		'change select[name="is_preceptor"]': '_onChangeIsPreceptor',
		'input .search-input': '_onSearchInput',
		'keyup .search-input': '_onSearchInput',
    },
 
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
		this._restoreSettings();
        return def;
    },

	_onSearchInput: function(ev) {
		var searchValue = $(ev.currentTarget).val().toLowerCase();
		var $tableRows = $('table tbody tr');
		
		if (searchValue === '') {
			$tableRows.show();
		} else {
			$tableRows.each(function() {
				var $row = $(this);
				var name = $row.find('td:first').text().toLowerCase();
				var email = $row.find('td:nth-child(2)').text().toLowerCase();
				var mobile = $row.find('td:nth-child(3)').text().toLowerCase();
				
				if (name.includes(searchValue) || email.includes(searchValue) || mobile.includes(searchValue)) {
					$row.show();
				} else {
					$row.hide();
				}
			});
		}
	},

	_onRestrictInput: function (ev) {
		ev.preventDefault();
	},
	
	_restrictSpecialCharacter(e) {  
	    var k;  
	    document.all ? k = e.keyCode : k = e.which;  
	    return ((k > 64 && k < 91) || (k > 96 && k < 123) || k == 9 || k == 8 || k == 32 || (k >= 48 && k <= 57));  
	}, 
	
	_insertCardNumberBlankSpace: function (e) {
		var restrictSpecialChar = this._restrictSpecialCharacter(e)
  		e.target.value = e.target.value.replace(/[^\dA-Z]/g, '').replace(/(.{4})/g, '$1 ').trim();
		return restrictSpecialChar;
	},

	_onClickDeletePartner: function (e) {
		var self = this;
		
		var def = new Promise(function (resolve, reject) {
			var message = _t("Are you sure you want to delete this record?");
			
			var dialog = Dialog.confirm(self, message, {
				title: _t("Confirmation"),
				confirm_callback: function() {
					var partner_id = $(e.target).attr('id');
					var deleted_partner_ids = [partner_id];
	
					var form_values = {
						'deleted_partner_ids': deleted_partner_ids
					};
	
					ajax.post('/delete_family_members', form_values)
						.then(function (result) {
							if (result === "deleted") {
								Dialog.alert(self, _t("Record has been deleted successfully."), {
									confirm_callback: function() {
										$(window.location).attr('href', "/family/");
									},
								});
							} else if (result === "current_user") {
								Dialog.alert(null, _t("Please contact Administrator to delete the record."));
							} else if (result === "cannot_delete") {
								Dialog.alert(null, _t("You can delete only Rejected and Not Yet Submitted records. If you have assigned an RFID card from Ashram Office, please contact Ashram office for deleting this record."));
							} else if (result === "no_records") {
								Dialog.alert(null, _t("Record does not exist."));
							}
						})
						.guardedCatch(function () {
							console.log("Error occurred during deletion.");
							Dialog.alert(self, _t("An error occurred while attempting to delete the record. Please try again later."));
						});
				},
				cancel_callback: reject,
			});
	
			dialog.on('closed', self, reject);
		});
	},
	
	_onChangeRelationType: function (ev) {
		var relation_type = this.$('select[name="relation_type"]');
		if(relation_type.val() == 'Other'){
			$('.relation_other_class').removeClass('d-none');
		}
		else{
			$('.relation_other_class').addClass('d-none');
		}
	},

	_adaptWorkDepartmentAddressForm: function () {
		var work_profile = document.getElementById("work_profile_id_field");
		if(typeof work_profile !== 'undefined' && work_profile !== null) {
			var selected_work_profile = work_profile.options[work_profile.selectedIndex].text;
			if(selected_work_profile.trim() != 'Resident'){
				$('.department').removeClass('d-none');
				$('.employee_id').removeClass('d-none');
			}
			else{
				document.getElementById("department_id").value = "";
			    document.getElementById("employee_id_id").value = "";
				$('.department').addClass('d-none');
				$('.employee_id').addClass('d-none');
			}
		}
    },
	
	_onWorkProfileChange: function () {
		this._adaptWorkDepartmentAddressForm();
	},

	_onVoterIdChange: function (ev) {
		var $target = $(ev.currentTarget);
		var selectedValue = this.$('select[name="do_you_need_voter_id_in_kanha"]').val();
		if (selectedValue === 'Yes') {
			$('#tab-kanha_voter_id').show();
			$('#voter_details_div').show();
			$('#collapse-kanha_voter_id').collapse('show');
			this._enableMandatoryFields();
		} else if (selectedValue === 'No') {
			$('#tab-kanha_voter_id').hide();
			$('#kanha_voter_id_info').hide();
			$('#voter_details_div').hide();
			$('#kanha_address').focus();
			$('#collapse-kanha_voter_id').collapse('hide');
			this._disableMandatoryFields();
			$('#collapse-kanha_voter_id').collapse('hide');
		}
	},

	_disableMandatoryFields: function () {
		$('.col-lg-8 input[required], .col-lg-8 select[required]').each(function () {
			$(this).attr('data-original-required', 'true');
			$(this).prop('required', false);
		});
	},

	_enableMandatoryFields: function () {
		$('.col-lg-8 input, .col-lg-8 select').each(function () {
			if ($(this).attr('data-original-required') === 'true') {
				$(this).prop('required', true);
			} else {
				$(this).prop('required', false);
			}
		});
	},

	_restoreSettings: function () {
		var selectedValue = this.$('select[name="do_you_need_voter_id_in_kanha"]').val();
		if (selectedValue === 'No') {
			$('#tab-kanha_voter_id').hide();
			$('#kanha_voter_id_info').hide();
			this._disableMandatoryFields();
		} else {
			$('#tab-kanha_voter_id').show();
			$('#kanha_voter_id_info').show();
		}
	},

    _onChangeVoterAddressToKanha: function (ev) {
		document.getElementById("application_type_field").value = "";
        $(ev.currentTarget).closest('form').find('select[name="application_type"]').trigger('change');
	
		var voter_is_there = this.$('select[id="already_have_kanha_voter_id_field"]');
		var voter_address_change = this.$('select[name="change_voter_id_address"]');
		if(voter_address_change.val() == 'Yes'){
			$('.voter_id_tab').removeClass('d-none');
			
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
			$('.voter_application_type').removeClass('d-none');
			$('#application_type_field').attr('required', true);

			var transfer_application = '<option value="Transfer Application">Transfer Application</option>'
			if(voter_is_there.val() == 'Yes'){
				$('#application_type_field').empty().append(transfer_application);
				$('#application_type_field').change()
			}
		}
		else{
			var is_voter_tab_active = $('a.voter_id_tab').hasClass('active');
			$('.voter_id_tab').addClass('d-none');
			
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

    _onChangeAlreadyHaveKanhaVoterID: function (ev) {
		document.getElementById("need_new_kanha_voter_id_field").value = "";
        $(ev.currentTarget).closest('form').find('select[name="need_new_kanha_voter_id"]').trigger('change');

		var already_have_kanha_voter_id = this.$('select[name="already_have_kanha_voter_id"]');
		if(already_have_kanha_voter_id.val() == 'Yes'){
			$('.need_new_kanha_voter_id').addClass('d-none');
			$('#need_new_kanha_voter_id_field').removeAttr('required');
			$('.kanha_voter_id_number').removeClass('d-none');
			$('#kanha_voter_id_number_field').attr('required', true);
			$('.kanha_voter_id_image').removeClass('d-none');
			$('.kanha_voter_id_back_image').removeClass('d-none');
			$('.change_voter_id_address').removeClass('d-none');
		}
		else if(already_have_kanha_voter_id.val() == 'No'){
			$('#change_voter_id_address_field').val("");
			$('#change_voter_id_address_field').change();
			$('.kanha_voter_id_number').addClass('d-none');
			$('#kanha_voter_id_number_field').removeAttr('required');
			$('.kanha_voter_id_image').addClass('d-none');
			$('#kanha_voter_id_image_field').removeAttr('required');
			$('.kanha_voter_id_back_image').addClass('d-none');
			$('#kanha_voter_id_back_image_field').removeAttr('required');
			$('.need_new_kanha_voter_id').removeClass('d-none');
			$('#need_new_kanha_voter_id_field').attr('required', true);
			$('.change_voter_id_address').addClass('d-none');
		}
		else{
			$('.need_new_kanha_voter_id').addClass('d-none');
			$('#need_new_kanha_voter_id_field').removeAttr('required');
			$('.kanha_voter_id_number').addClass('d-none');
			$('#kanha_voter_id_number_field').removeAttr('required');
			$('.kanha_voter_id_image').addClass('d-none');
			$('#kanha_voter_id_image_field').removeAttr('required');
			$('.kanha_voter_id_back_image').addClass('d-none');
			$('#kanha_voter_id_back_image_field').removeAttr('required');
			$('.change_voter_id_address').addClass('d-none');
		}
    },

    _onChangeNeedNewKanhaVoterID: function (ev) {
		document.getElementById("application_type_field").value = "";
        $(ev.currentTarget).closest('form').find('select[name="application_type"]').trigger('change');

		var need_new_kanha_voter_id = this.$('select[name="need_new_kanha_voter_id"]');
		if(need_new_kanha_voter_id.val() == 'Yes'){
			$('.voter_application_type').removeClass('d-none');
			$('#application_type_field').attr('required', true);
			var new_application = '<option value="New Application">New Application</option>'
			$('#application_type_field').empty().append(new_application);
			$('#application_type_field').change()
		}
		else{
			$('.voter_application_type').addClass('d-none');
			$('#application_type_field').removeAttr('required');
		}
    },

	_onCitizenshipChange: function () {
		var citizenship = this.$('select[name="citizenship"]');
		if(citizenship.val() == 'Overseas'){
			$('#change_voter_id_address_field').val("");
			$('#change_voter_id_address_field').change();
			$('#already_have_kanha_voter_id_field').val("")
			$('#already_have_kanha_voter_id_field').change()
			$('.passport_field').removeClass('d-none');
			$('#passport_number_input').attr('required', true);
			$('.passport_front_image_div').removeClass('d-none');
			$('.passport_back_image_div').removeClass('d-none');
			$('#passport_front_image_file').attr('required', true);
			$('#passport_back_image_file').attr('required', true);
			$('.indian_visa_div').removeClass('d-none');
			$('#indian_visa_file').attr('required', true);

			$('#aadhaar_card_number_field').removeAttr('required');
			$("label[for='Aadhaar Card Number']").next(".s_website_form_mark").addClass('d-none')
			$("label[for='Aadhar Card Front']").next(".s_website_form_mark").addClass('d-none')
			$("label[for='Aadhar Card Back']").next(".s_website_form_mark").addClass('d-none')
			$('#adhar_card_file_front').removeAttr('required');
			$("#adhar_card_file_front").next(".s_website_form_mark").addClass('d-none')
			$('#adhar_card_file_back').removeAttr('required');
			$("#adhar_card_file_back").next(".s_website_form_mark").addClass('d-none')
			
			var is_kanha_voter_tab_active = $('a#tab-kanha_voter_id').hasClass('active');
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
		}
		else{
			$('.passport_field').addClass('d-none');
			$('#passport_number_input').removeAttr('required');
			$('.passport_front_image_div').addClass('d-none');
			$('.passport_back_image_div').addClass('d-none');
			$('#passport_front_image_file').removeAttr('required');
			$('#passport_back_image_file').removeAttr('required');
			$('.indian_visa_div').addClass('d-none');
			$('#indian_visa_file').removeAttr('required');
			
			$("label[for='Aadhar Card Front']").next(".s_website_form_mark").removeClass('d-none')
			$("label[for='Aadhar Card Back']").next(".s_website_form_mark").removeClass('d-none')
			$('#aadhaar_card_number_field').attr('required', true);
			$('#adhar_card_file_front').attr('required', true);
			$('#adhar_card_file_back').attr('required', true);
			
			$('#tab-kanha_voter_id').removeClass('d-none');
			$('#pane-kanha_voter_id').removeClass('d-none');
			
			$('#birth_country_id_field').attr('required', true);
			$('#birth_state_id_field').attr('required', true);
			$('#birth_district_field').attr('required', true);
			$('#birth_town_field').attr('required', true);
			$('#already_have_kanha_voter_id_field').attr('required', true);
		}
    },

	 _onUploadPassportFrontImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is"+ fileSizeFormatted +"MB. file size cannot exceed 5MB.");
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

	 _onUploadPassportBackImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is"+ fileSizeFormatted +"MB. file size cannot exceed 5MB.");
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

	 _onUploadIndianVisa: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is"+ fileSizeFormatted +"MB. file size cannot exceed 5MB.");
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
	
	_onUploadPassportPhoto: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0]
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is"+ fileSizeFormatted +"MB. file size cannot exceed 5MB.");
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
	
	_onUploadKanhaVoterIdImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0];
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is"+ fileSizeFormatted +"MB. file size cannot exceed 5MB.");
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
	
	_onUploadKanhaVoterIdBackImage: function (ev) {
		var files = ev.target.files;
		if (!files.length) {
            return;
        }
		var file = files[0];
		var mimeType = file.type
		if(mimeType.indexOf("image/") == 0){
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is"+ fileSizeFormatted +"MB. file size cannot exceed 5MB.");
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
	
	_onBrowseFile: function (ev) {
		ev.preventDefault();
		var fileupload = $(ev.target).attr('fileupload')
        $(ev.currentTarget).closest('form').find('.'+fileupload).trigger('click');
 	},

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
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is"+ fileSizeFormatted +"MB. file size cannot exceed 5MB.");
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
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is"+ fileSizeFormatted +"MB. file size cannot exceed 5MB.");
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
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is" + fileSizeFormatted + "MB. file size cannot exceed 5MB.");
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
		  	var fileSize = file.size / 1024 / 1024;
	  		if (fileSize > 5) {
				var fileSizeFormatted = fileSize.toFixed(2);
				Dialog.alert(null, "File is too big. Your File size is"+ fileSizeFormatted +"MB. file size cannot exceed 5MB.");
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
 	
    _onClearFile: function (ev) {
		var fileupload_input = $(ev.target).attr('fileupload_input')
		var filename_input = $(ev.target).attr('filename_input')
        var $form = $(ev.currentTarget).closest('form');
        $form.find('.'+filename_input).val('');
		$form.find('.'+fileupload_input).val('');
    },

    _adaptBirthStateAddressForm: function () {
        var $birth_country = this.$('select[name="birth_country_id"]');
        var birthCountryID = ($birth_country.val() || 0);
        this.$birthStateOptions.detach();
        var $displayedBirthState = this.$birthStateOptions.filter('[data-country_id=' + birthCountryID + ']');
        var nb = $displayedBirthState.appendTo(this.$birthState).show().length;

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

    _onKanhaLocationChange: function () {
        this._adaptKanhaHouseNumberStateAddressForm();
    },

	 _adaptKanhaHouseNumberStateAddressForm: function () {
		var $kanha_location = this.$('select[name="kanha_location_id"]');
        var KanhaLocationID = ($kanha_location.val() || 0);
        this.$kanhaHouseNumberOptions.detach();
        var $displayedKanhaHouseNumber = this.$kanhaHouseNumberOptions.filter('[data-kanha_location_id=' + KanhaLocationID + ']');
        var nb = $displayedKanhaHouseNumber.appendTo(this.$kanhaHouseNumber).show().length;
    },

    _onBirthCountryChange: function () {
        this._adaptBirthStateAddressForm();
    },

    _adaptAddressForm: function () {
        var $country = this.$('select[name="country_id"]');
        var countryID = ($country.val() || 0);
        this.$stateOptions.detach();
        var $displayedState = this.$stateOptions.filter('[data-country_id=' + countryID + ']');
        var nb = $displayedState.appendTo(this.$state).show().length;
    },

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
		
		ajax.post('/vehicle_details_form', vehicle_vals).then(function (modal) {
	 		var $modal = $(modal);
            $modal.modal({backdrop: 'static', keyboard: false});
            $modal.appendTo('body').modal();
			
			$modal.on('click', '.save_vehicle_line', function (ev) {
				$(".save_vehicle_line").attr('disabled',true)
				var vehicle_number = $modal.find('input[name="vehicle_number"]').val();
				var vehicle_owner = $modal.find('input[name="vehicle_owner"]').val();
				var vehicle_type = $modal.find('select[name="vehicle_type"]').val();
				var fasttag_rfid_no = $modal.find('input[name="fasttag_rfid_no"]').val();

				if(id){
					$('#vehicle_table tr#'+id).find('.vehicle_number').text(vehicle_number)
					$('#vehicle_table tr#'+id).find('.vehicle_owner').text(vehicle_owner)
					$('#vehicle_table tr#'+id).find('.vehicle_type').text(vehicle_type)
					$('#vehicle_table tr#'+id).find('.fasttag_rfid_no').text(fasttag_rfid_no)
				}
				else{
					if(vehicle_number || vehicle_owner || vehicle_type || fasttag_rfid_no)
					{
						var vehicle_table = document.getElementById('vehicle_table');
					    var index = vehicle_table.rows.length - 1;
						var newRow=document.getElementById('vehicle_table').insertRow(index);
						
						if(!$row.hasClass('empty-row')){
							$row.remove();
						}
						newRow.innerHTML = '<td class="d-none"></td><td name="vehicle_number" class="vehicle_number">'+vehicle_number+'</td><td name="vehicle_owner">'+vehicle_owner+'</td><td name="vehicle_type">'+vehicle_type+'</td><td name="fasttag_rfid_no">'+fasttag_rfid_no+'</td><td class="text-right"><button type="button" class="btn btn-secondary fa fa-pencil mr-1 vehicle_edit_new" title="Edit" aria-label="Edit"/><button type="button" class="btn btn-secondary fa fa-trash-o vehicle_clear" title="Clear" aria-label="Clear"/></td>';
					}
				}
			 	$modal.modal('hide');	
            });
		})
	},

	_onSaveForm: function (e, is_submit) {
		try {
			console.log("Initiating form save process...");
			$("#loading").removeClass('hide');
	
			var $form = $(e.currentTarget).closest('form');
			var self = this;
			var form_values = {};
	
			this.form_fields = $form.serializeArray();
			console.log("Serialized form fields:", this.form_fields);
	
			this.$target.find('input[type=file]').each(function (outer_index, input) {
				$.each($(input).prop('files'), function (index, file) {
					self.form_fields.push({
						name: `${input.name}[${outer_index}][${index}]`,
						value: file
					});
				});
			});
	
			_.each(this.form_fields, function (input) {
				if (input.name in form_values) {
					form_values[input.name] = Array.isArray(form_values[input.name])
						? [...form_values[input.name], input.value]
						: [form_values[input.name], input.value];
				} else {
					form_values[input.name] = input.value || '';
				}
			});
			console.log("Form values after processing:", form_values);
	
			this.$target.find('.s_website_form_field:not(.s_website_form_custom) .s_website_form_date, .s_website_form_datetime').each(function () {
				var dateInput = $(this).find('input');
				if (dateInput.length > 0) {
					var date = $(this).datetimepicker('viewDate').clone().locale('en');
					var format = $(this).hasClass('s_website_form_datetime') ? 'YYYY-MM-DD HH:mm:ss' : 'YYYY-MM-DD';
					form_values[dateInput.attr('name')] = date.utc().format(format);
				}
			});
			console.log("Form values after date formatting:", form_values);
	
			var vehicle_details = {};
			var vehicle_new_lines = [];
			$('#vehicle_table tbody tr:not(:last-child)').each(function () {
				var vehicle_vals = {};
				var vehicle_row_id = $(this).attr('id');
	
				$(this).find('td').each(function () {
					var name = $(this).attr('name');
					var value = $(this).html().trim();
					if (name) {
						vehicle_vals[name] = value;
					}
				});
	
				if (vehicle_row_id) {
					vehicle_details[parseInt(vehicle_row_id)] = vehicle_vals;
				} else {
					vehicle_new_lines.push(vehicle_vals);
				}
			});
			form_values['vehicle_details_ids'] = JSON.stringify(vehicle_details);
			form_values['vehicle_new_lines'] = JSON.stringify(vehicle_new_lines);
			form_values['is_submit'] = is_submit;
			console.log("Processed vehicle details:", vehicle_details);
			console.log("New vehicle lines:", vehicle_new_lines);
	
			var birth_country = document.getElementById("birth_country_id_field");
			if (birth_country) {
				var selected_country = birth_country.options[birth_country.selectedIndex].text;
				if (selected_country.trim() === 'India') {
					form_values['birth_state_textfield'] = '';
				}
			}
	
			ajax.post($form.attr('action') + ($form.data('force_action') || $form.data('model_name')), form_values)
				.then(function (result_data) {
					$("#loading").addClass('hide');
					self.$target.find('.family_website_form_submit')
						.removeAttr('disabled')
						.removeClass('disabled');
	
					try {
						result_data = JSON.parse(result_data);
					} catch (error) {
						console.error("Error parsing result data:", error);
						self.update_status('error', "Invalid server response.");
						return;
					}
	
					if (!result_data.id) {
						let errorMessage = result_data.error_message || "An unexpected error occurred while submitting the form.";
						self.update_status('error', errorMessage);
	
						if (result_data.error_fields) {
							self.check_error_fields_save(Object.keys(result_data.error_fields));
							$("html, body").animate({ scrollTop: 0 }, "slow");
						}
					} else {
						let successMode = $form[0].dataset.successMode || ($form.attr('data-success_page') ? 'redirect' : 'nothing');
						let successPage = $form[0].dataset.successPage || $form.attr('data-success_page');
	
						switch (successMode) {
							case 'redirect':
								if (successPage.charAt(0) === "#") {
									dom.scrollTo($(successPage)[0], { duration: 500 });
								} else {
									$(window.location).attr('href', is_submit ? successPage : "/family/");
								}
								break;
	
							case 'message':
								self.$target.addClass('d-none');
								self.$target.parent().find('.s_website_form_end_message').removeClass('d-none');
								break;
	
							default:
								self.update_status('success', "Form submitted successfully!");
								break;
						}
					}
				})
				.guardedCatch(function (error) {
					console.error("Form submission error:", error);
					self.update_status('error', "An error occurred while submitting the form. Please try again later.");
				});
	
		} catch (error) {
			console.error("Error in _onSaveForm function:", error);
			alert("An issue occurred while processing the form. Check the console for more details.");
		}
	},	
	
	_validateForm: function (e) {
        e.preventDefault();
		
        var self = this;
        this.$target.find('.family_website_form_result').html();
		var is_form_valid = Object.keys(self.check_error_fields({}))
		if (is_form_valid == 'false') {
			var missing_fields = Object.values(self.check_error_fields({}))
            self.update_status('error', _t("Please fill in the form correctly."+'\n'.concat(missing_fields.join())));
			return false;
        }
		return true;
    },

	_clearFormStatus: function (e) {
		this.$('#form_result_error').addClass('d-none');
		
		this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { 
			var $field = $(field);
        	$field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
 		});
	},
	
	_onClickSave: function (e, is_submit=false) {
		this._clearFormStatus(e);
		var citizenship = $('.citizenship').val();
		var aadhaar_card_number = $('#aadhaar_card_number_field').val();
		var passport_number = $('#passport_number_input').val();
		var name_input = $('#name_input').val();
		var blood_group_input = $('#blood_group_id').val();
		if(!blood_group_input){
			$('#blood_group_id').addClass('is-invalid');
			this.update_status('error', _t("Blood Group is Mandatory to Save Record!"));
			$("html, body").animate({ scrollTop: 0 }, "slow");
			return false;
		}
		if(!name_input){
			$('#name_input').addClass('is-invalid');
			this.update_status('error', _t("Name is Mandatory to Save Record!"));
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
        
        this.$target.find('.form-field, .s_website_form_field').each(function (k, field) {
            var $field = $(field);
            var field_name = $field.find('.col-form-label').attr('for');

            var inputs = $field.find('.s_website_form_input, .o_website_form_input').not('#editable_select');
            var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
                if (input.required && input.type === 'checkbox') {
                    var checkboxes = _.filter(inputs, function (input) {
                        return input.required && input.type === 'checkbox';
                    });
                    return !_.any(checkboxes, checkbox => checkbox.checked);

                } else if ($(input).hasClass('s_website_form_date') || $(input).hasClass('o_website_form_date')) {
                    if (!self.is_datetime_valid(input.value, 'date')) {
                        return true;
                    }
                } else if ($(input).hasClass('s_website_form_datetime') || $(input).hasClass('o_website_form_datetime')) {
                    if (!self.is_datetime_valid(input.value, 'datetime')) {
                        return true;
                    }
                }
                return !input.checkValidity();
            });

            $field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
            
			if (invalid_inputs.length || error_fields[field_name]) {
				if(field_name != undefined){
					missing_fields.push(field_name)
				}
                $field.addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
				
                if (_.isString(error_fields[field_name])) {
                    $field.popover({content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top'});
                    $field.data("bs.popover").config.content = error_fields[field_name];
                    $field.popover('show');
                }
                form_valid = false;
            }
        });
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

    _onChangeIsPreceptor: function (ev) {
		var is_preceptor = this.$('select[name="is_preceptor"]');
		if(is_preceptor.val() == 'Yes'){
			$('#abhyasi_id_id').attr('required', true);
		}
		else if(is_preceptor.val() == 'No'){
			$('#abhyasi_id_id').removeAttr('required');
		}
		else{
			$('#abhyasi_id_id').removeAttr('required');
		}
    },

    update_status: function (status, message) {
		console.log("Inside Update Status", status, message);
	
		message = message || '';
		
		var $result = this.$('.family_website_form_result');
	
		this.$('#form_result_error').addClass('d-none');
		this.$('#form_result_success').addClass('d-none');
	
		if (status === 'error') {
			this.$('#form_result_error').removeClass('d-none');
			if (!message) {
				message = _t("An error has occurred, the form has not been sent.");
			}
		} else if (status === 'success') {
			this.$('#form_result_success').removeClass('d-none');
		}
	
		if (status !== 'success') {
			this.$target.find('.family_website_form_submit')
				.removeAttr('disabled')
				.removeClass('disabled');
		}
	
		$result.html(message);
	},
	
});
});