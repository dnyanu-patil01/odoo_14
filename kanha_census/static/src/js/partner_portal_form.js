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
        'change input[name="members_count"]': '_onMembersCountChange',
        'input input[name="members_count"]': '_onMembersCountInput',
        'keypress input[name="members_count"]': '_onMembersCountKeypress',
        'change select[name="property_owner"]': '_onChangePropertyOwner',
        'change select[name="residence_type"]': '_onChangeResidenceType',
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
        'click .govt_id_proof_edit': '_onBrowseFile',
        'change .govt_id_proof_upload': '_onUploadGovtIdProof',
        'click .govt_id_proof_browse': '_onBrowseFile',
        'click .govt_id_proof_clear': '_onClearFile',
        'click .any_gov_id_proof_edit': '_onBrowseFile',
        'change .any_gov_id_proof_upload': '_onUploadGovtIdProof',
        'click .any_gov_id_proof_browse': '_onBrowseFile',
        'click .any_gov_id_proof_clear': '_onClearFile',
        'keypress #govt_id_proof_file': '_onRestrictInput',
        'keydown #govt_id_proof_file': '_onRestrictInput',
        'keypress #any_gov_id_proof_file': '_onRestrictInput',
        'keydown #any_gov_id_proof_file': '_onRestrictInput',
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
        'change select[name="has_voter_id_in_kanha"]': '_onHasVoterIdChange',
        'change select[name="is_preceptor"]': '_onChangeIsPreceptor',
        'input .search-input': '_onSearchInput',
        'keyup .search-input': '_onSearchInput',
        'input input[name="name"]': '_onNameChange',
        'input input[name="surname"]': '_onSurnameChange',
    },

    _onNameChange: function(ev) {
        this._syncFullNamePassport();
    },

    _onSurnameChange: function(ev) {
        this._syncFullNamePassport();
    },

     _syncFullNamePassport: function() {
        var name = $('input[name="name"]').val() || '';
        var surname = $('input[name="surname"]').val() || '';
        var fullNamePassportField = $('input[name="full_name_passport"]');
        
        if (name && surname) {
            fullNamePassportField.val(name + ' ' + surname);
        } else if (name && !surname) {
            fullNamePassportField.val(name);
        } else if (!name && surname) {
            fullNamePassportField.val(surname);
        } else {
            fullNamePassportField.val('');
        }
    },

    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.$target = this.$el;
        this.isFormSaved = false;
        window.generateFamilyMembers = this._generateFamilyRows.bind(this);
        window.togglePropertyOwnerFields = this.togglePropertyOwnerFields.bind(this);
    },

    start: function () {
        var def = this._super.apply(this, arguments);
        this.$target = this.$el;
        this.$birthState = this.$('select[name="birth_state_id"]');
        this.$birthStateOptions = this.$birthState.filter(':enabled').find('option:not(:first)');
        this._adaptBirthStateAddressForm();
        this.$state = this.$('select[name="state_id"]');
        this.$stateOptions = this.$state.filter(':enabled').find('option:not(:first)');
        this._adaptAddressForm();
        this.$kanhaHouseNumber = this.$('select[name="kanha_house_number_id"]');
        this.$kanhaHouseNumberOptions = this.$kanhaHouseNumber.filter(':enabled').find('option:not(:first)');
        this._adaptKanhaHouseNumberStateAddressForm();
        this._removeRequiredFields();
        this._initializeFamilyTable();
        this._initializePropertyOwnerFields();
        this._setIndianMandatoryFields();
        this._checkIfFormSaved();
        this._restoreSettings();
        this._restoreVoterIdData();
        this._restoreFamilyData();
        return def;
    },

    _checkIfFormSaved: function() {
    var partnerId = this.$('input[name="partner_id"]').val();
    var recordExists = this.$('input[name="record_exists"]').val();
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    if (partnerId && recordExists === 'true') {
        this.isFormSaved = true;
        
        if (applicationState && (applicationState === 'draft' || applicationState === 'approved_for_edit')) {
            this.isFormSaved = false;
        }
        
        if (this.isFormSaved) {
            this._restoreFamilyData();
            this._makeFormReadonly();
            this._hideAllFileUploads();
        }
    }
},
    _hideAllFileUploads: function() {
        var applicationState = this.$('input[name="application_state"]').val() || 
                            this.$('select[name="application_state"]').val() ||
                            this.$('.application_state').val();
        
        if (applicationState && (applicationState === 'draft' || applicationState === 'approved_for_edit')) {
            return;
        }
        
        $('.adhar_file_edit, .adhar_file_browse').hide();
        $('.adhar_file_back_side_edit, .adhar_file_back_side_browse').hide();
        $('.age_proof_edit, .age_proof_browse').hide();
        $('.address_proof_edit, .address_proof_browse').hide();
        $('.indian_visa_edit, .indian_visa_browse').hide();
        $('.passport_photo_edit, .passport_photo_browse').hide();
        $('.passport_front_image_edit, .passport_front_image_browse').hide();
        $('.passport_back_image_edit, .passport_back_image_browse').hide();
        $('.kanha_voter_id_image_browse, .kanha_voter_id_image_edit').hide();
        $('.kanha_voter_id_back_image_browse, .kanha_voter_id_back_image_edit').hide();
        $('.govt_id_proof_edit, .govt_id_proof_browse').hide();
        $('.any_gov_id_proof_edit, .any_gov_id_proof_browse').hide();
        
        $('#any_gov_id_proof_field').hide();
        
        $('input[type="file"]').hide();
        $('.file-upload-container, .upload-section, .custom-file').hide();
        $('input[type="file"]').prop('disabled', true);
    },


    _disableAllFileUploads: function() {
        var applicationState = this.$('input[name="application_state"]').val() || 
                            this.$('select[name="application_state"]').val() ||
                            this.$('.application_state').val();
        
        if (applicationState && (applicationState === 'draft' || applicationState === 'approved_for_edit')) {
            return;
        }
        
        $('input[type="file"]').each(function() {
            $(this).prop('disabled', true).hide().off('change');
        });
        
        $('.file-upload-container, .upload-section').each(function() {
            $(this).addClass('upload-disabled').css({
                'pointer-events': 'none',
                'opacity': '0.6'
            });
        });
    },
    _onUploadGovtIdProof: function (ev) {
        if (this.isFormSaved) {
            ev.preventDefault();
            return;
        }
        
        var files = ev.target.files;
        if (!files.length) {
            return;
        }
        var file = files[0];
        var mimeType = file.type;
        
        if(mimeType !== "image/jpeg" && mimeType !== "image/jpg"){
            Dialog.alert(null, "Only JPG format is allowed.");
            ev.target.value = "";
            return;
        }
        
        var fileSize = file.size / 1024;
        if (fileSize > 500) {
            var fileSizeFormatted = fileSize.toFixed(2);
            Dialog.alert(null, "File is too big. Your File size is " + fileSizeFormatted + "KB. File size cannot exceed 500KB.");
            ev.target.value = "";
            var $form = $(ev.currentTarget).closest('form');
            var filename_input = $(ev.target).attr('filename_input');
            $form.find('.'+filename_input).val('');
        }
        else{
            var file_name = ev.target.files[0].name;
            var $form = $(ev.currentTarget).closest('form');
            var filename_input = $(ev.target).attr('filename_input');
            $form.find('.'+filename_input).val(file_name);
        }
    },
    _makeFormReadonly: function() {
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    if (applicationState && (applicationState === 'draft' || applicationState === 'approved_for_edit')) {
        return;
    }
    
    this._makeFamilyDetailsReadonly();
    this._makeDocumentsReadonly();
    this._makeMainFormReadonly();
},
    _makeFamilyDetailsReadonly: function() {
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    if (applicationState && (applicationState === 'draft' || applicationState === 'approved_for_edit')) {
        return;
    }
    
    var citizenship = $('select[name="citizenship"]').val();
    var isOverseas = (citizenship === 'Overseas');
    var $tableBody = isOverseas ? $('#overseas-family-table-body') : $('#family-table-body');
    
    if ($tableBody.length === 0) {
        return;
    }
    
    $tableBody.find('input, select').each(function() {
        $(this).prop('disabled', true).css({
            'background-color': '#e9ecef',
            'color': '#6c757d',
            'cursor': 'not-allowed'
        });
    });
    
    $('.vehicle_add_new, .vehicle_edit_new, .vehicle_edit_exist, .vehicle_clear').hide();
},
	_makeMainFormReadonly: function() {
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    if (applicationState && (applicationState === 'draft' || applicationState === 'approved_for_edit')) {
        return;
    }
    
    this.$('input:not([type="hidden"]), select, textarea').each(function() {
        var $element = $(this);
        var isSearchInput = $element.hasClass('search-input');
        
        if (!isSearchInput) {
            if ($element.is('select')) {
                $element.prop('disabled', true);
                $element.css({
                    'pointer-events': 'none',
                    'background-color': '#e9ecef',
                    'color': '#6c757d',
                    'opacity': '1',
                    'cursor': 'not-allowed'
                });
            } else {
                $element.prop('readonly', true);
                $element.css({
                    'background-color': '#e9ecef',
                    'color': '#6c757d',
                    'cursor': 'not-allowed'
                });
            }
        }
    });
    
    $('.family_website_form_submit, .family_website_form_save').hide();
},

    _makeMainFormReadonly: function() {
        var applicationStatus = this.$('input[name="application_status"]').val() || 
                               this.$('select[name="application_status"]').val();
        
        if (applicationStatus && (applicationStatus === 'draft' || applicationStatus === 'to_approve' || applicationStatus === 'approved_for_edit')) {
            return;
        }
        
        this.$('input:not([type="hidden"]), select, textarea').each(function() {
            var $element = $(this);
            var isSearchInput = $element.hasClass('search-input');
            
            if (!isSearchInput) {
                if ($element.is('select')) {
                    $element.prop('disabled', true);
                    $element.css({
                        'pointer-events': 'none',
                        'background-color': '#e9ecef',
                        'color': '#6c757d',
                        'opacity': '1',
                        'cursor': 'not-allowed'
                    });
                } else {
                    $element.prop('readonly', true);
                    $element.css({
                        'background-color': '#e9ecef',
                        'color': '#6c757d',
                        'cursor': 'not-allowed'
                    });
                }
            }
        });
        
        $('.family_website_form_submit, .family_website_form_save').hide();
    },


    _makeDocumentsReadonly: function() {
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    if (applicationState && (applicationState === 'draft' || applicationState === 'approved_for_edit')) {
        return;
    }
    
    $('.adhar_file_edit, .adhar_file_browse, .adhar_file_clear').hide();
    $('.adhar_file_back_side_edit, .adhar_file_back_side_browse, .adhar_file_back_side_clear').hide();
    $('.age_proof_edit, .age_proof_browse, .age_proof_clear').hide();
    $('.address_proof_edit, .address_proof_browse, .address_proof_clear').hide();
    $('.indian_visa_edit, .indian_visa_browse, .indian_visa_clear').hide();
    $('.passport_photo_edit, .passport_photo_browse, .passport_photo_clear').hide();
    $('.passport_front_image_edit, .passport_front_image_browse, .passport_front_image_clear').hide();
    $('.passport_back_image_edit, .passport_back_image_browse, .passport_back_image_clear').hide();
    $('.kanha_voter_id_image_browse, .kanha_voter_id_image_edit, .kanha_voter_id_image_clear').hide();
    $('.kanha_voter_id_back_image_browse, .kanha_voter_id_back_image_edit, .kanha_voter_id_back_image_clear').hide();
    $('.govt_id_proof_edit, .govt_id_proof_browse, .govt_id_proof_clear').hide();
    $('.any_gov_id_proof_edit, .any_gov_id_proof_browse, .any_gov_id_proof_clear').hide();
    
    $('#any_gov_id_proof_field').hide();
    $('input[name="any_gov_id_proof"]').prop('disabled', true).hide();
    
    $('input[type="file"]').prop('disabled', true).hide();
    $('.file-upload-wrapper, .custom-file, .file-upload-container, .upload-section').hide();
    $('input[type="file"]').off('change');
},


    _setIndianMandatoryFields: function() {
    $('#residence_type_field').attr('required', true);
    $("label[for='residence_type'] .s_website_form_mark").remove();
    $("label[for='residence_type']").append('<span class="s_website_form_mark"> *</span>');
    
    var citizenship = this.$('select[name="citizenship"]').val();
    if (citizenship === 'Indian' || !citizenship) {
        $('#has_voter_id_in_kanha_field').attr('required', true);
        $('#members_count_id').attr('required', true);
        
        $("label[for='has_voter_id_in_kanha'] .s_website_form_mark").remove();
        $("label[for='has_voter_id_in_kanha']").append('<span class="s_website_form_mark"> *</span>');
    }
    },

   _initializePropertyOwnerFields: function() {
        var residenceType = this.$('select[name="residence_type"]').val();
        this._togglePropertyOwnerFieldsBasedOnResidence(residenceType);
    },

    _onChangeResidenceType: function(ev) {
        var residenceType = $(ev.currentTarget).val();
        this._togglePropertyOwnerFieldsBasedOnResidence(residenceType);
        
        var propertyOwnerSelect = this.$('select[name="property_owner"]');
        if (propertyOwnerSelect.length) {
            propertyOwnerSelect.val('');
            propertyOwnerSelect.trigger('change');
        }
    },

    _togglePropertyOwnerFieldsBasedOnResidence: function(residenceType) {
        var propertyOwnerNameField = $('#property_owner_name_field');
        var propertyOwnerEmailField = $('#property_owner_email_field');
        var propertyOwnerPhoneField = $('#property_owner_phone_field');
        
        if (residenceType === 'Rented Place' || residenceType === 'Guest House') {
            propertyOwnerNameField.removeClass('d-none');
            propertyOwnerEmailField.removeClass('d-none');
            propertyOwnerPhoneField.removeClass('d-none');
            
            $('#property_owner_name_input').attr('required', true);
            $('#property_owner_email_input').attr('required', true);
            $('#property_owner_phone_input').attr('required', true);
        } else {
            propertyOwnerNameField.addClass('d-none');
            propertyOwnerEmailField.addClass('d-none');
            propertyOwnerPhoneField.addClass('d-none');
            
            $('#property_owner_name_input').removeAttr('required').val('');
            $('#property_owner_email_input').removeAttr('required').val('');
            $('#property_owner_phone_input').removeAttr('required').val('');
        }
    },

    _clearPropertyOwnerSubFields: function() {
        var propertyOwnerOtherDiv = document.querySelector('.property_owner_other');
        var propertyOwnerRelationDiv = document.querySelector('.property_owner_relation');
        
        if (propertyOwnerOtherDiv) {
            propertyOwnerOtherDiv.classList.add('d-none');
            var otherInput = propertyOwnerOtherDiv.querySelector('input');
            if (otherInput) {
                otherInput.value = '';
            }
        }
        
        if (propertyOwnerRelationDiv) {
            propertyOwnerRelationDiv.classList.add('d-none');
            var relationSelect = propertyOwnerRelationDiv.querySelector('select');
            if (relationSelect) {
                relationSelect.value = '';
            }
        }
    },

    togglePropertyOwnerFields: function(selectElement) {
        var value = selectElement ? selectElement.value : '';
        var propertyOwnerOtherDiv = document.querySelector('.property_owner_other');
        var propertyOwnerRelationDiv = document.querySelector('.property_owner_relation');
        
        if (propertyOwnerOtherDiv) {
            if (value === 'Other') {
                propertyOwnerOtherDiv.classList.remove('d-none');
            } else {
                propertyOwnerOtherDiv.classList.add('d-none');
                var otherInput = propertyOwnerOtherDiv.querySelector('input');
                if (otherInput) {
                    otherInput.value = '';
                }
            }
        }
        
        if (propertyOwnerRelationDiv) {
            if (value === 'Family Member') {
                propertyOwnerRelationDiv.classList.remove('d-none');
            } else {
                propertyOwnerRelationDiv.classList.add('d-none');
                var relationSelect = propertyOwnerRelationDiv.querySelector('select');
                if (relationSelect) {
                    relationSelect.value = '';
                }
            }
        }
    },

    _onChangePropertyOwner: function(ev) {
        this.togglePropertyOwnerFields(ev.currentTarget);
    },

    _initializeFamilyTable: function() {
        var self = this;
        setTimeout(function() {
            var membersCount = parseInt($('#members_count_id').val()) || 1;
            self._generateFamilyRows(membersCount);
        }, 100);
    },


     _generateInitialRow: function() {
        var citizenship = $('select[name="citizenship"]').val() || 'Indian';
        var isOverseas = (citizenship === 'Overseas');
        
        var $tableBody = isOverseas ? $('#overseas-family-table-body') : $('#family-table-body');
        if ($tableBody.length === 0) return;
        
        $tableBody.empty();
        
        var applicantName = $('input[name="name"]').val() || '';
        var applicantBloodGroup = $('select[name="blood_group"]').val() || '';
        var applicantGovtId = '';
        
        if (isOverseas) {
            applicantGovtId = $('input[name="passport_number"]').val() || $('input[name="govt_id_proof"]').val() || '';
        }
        
        var bloodGroupOptions = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB-', 'AB+'];
        
        var rowHtml = '<tr id="family-row-0">';
        
        var nameReadonly = this.isFormSaved ? ' readonly disabled' : '';
        var selectDisabled = this.isFormSaved ? ' disabled' : '';
        
        rowHtml += '<td><input type="text" class="form-control" name="family_member_name_0" placeholder="Enter Name" value="' + applicantName + '"' + nameReadonly + ' /></td>';
        rowHtml += '<td><select class="form-control" name="family_member_relation_0"' + selectDisabled + '><option value="Head" selected>Head</option></select></td>';
        
        rowHtml += '<td><select class="form-control" name="family_member_blood_group_0"' + selectDisabled + '><option value="">Select...</option>';
        bloodGroupOptions.forEach(function(bloodGroup) {
            var selected = (bloodGroup === applicantBloodGroup) ? ' selected' : '';
            rowHtml += '<option value="' + bloodGroup + '"' + selected + '>' + bloodGroup + '</option>';
        });
        rowHtml += '</select></td>';
        
        if (isOverseas) {
            rowHtml += '<td><input type="text" class="form-control" name="family_member_govt_id_0" placeholder="Enter Govt ID" value="' + applicantGovtId + '"' + nameReadonly + ' /></td>';
            var fileDisabled = this.isFormSaved ? ' disabled style="display:none;"' : '';
            rowHtml += '<td><input type="file" class="form-control" name="family_member_passport_photo_0" accept="image/jpeg,image/jpg"' + fileDisabled + ' /></td>';
            rowHtml += '<td><input type="file" class="form-control" name="family_member_address_proof_0" accept="image/jpeg,image/jpg"' + fileDisabled + ' /></td>';
        }
        
        rowHtml += '</tr>';
        
        $tableBody.append(rowHtml);
        this._syncApplicantData();
    },

    _onMembersCountKeypress: function(ev) {
        var applicationState = this.$('input[name="application_state"]').val() || 
                            this.$('select[name="application_state"]').val() ||
                            this.$('.application_state').val();
        
        if (this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit')) {
            ev.preventDefault();
            return false;
        }
        
        var charCode = ev.which || ev.keyCode;
        var char = String.fromCharCode(charCode);
        
        if (charCode === 8 || charCode === 9 || charCode === 46) {
            return true;
        }
        
        if (!/^[1-8]$/.test(char)) {
            ev.preventDefault();
            return false;
        }
        
        var currentValue = $(ev.currentTarget).val();
        if (currentValue.length >= 1) {
            ev.preventDefault();
            return false;
        }
        
        return true;
    },

    _onMembersCountInput: function(ev) {
        var applicationState = this.$('input[name="application_state"]').val() || 
                            this.$('select[name="application_state"]').val() ||
                            this.$('.application_state').val();
        
        if (this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit')) {
            return;
        }
        
        var value = $(ev.currentTarget).val();
        var sanitizedValue = value.replace(/[^1-8]/g, '');
        
        if (sanitizedValue.length > 1) {
            sanitizedValue = sanitizedValue.charAt(0);
        }
        
        if (value !== sanitizedValue) {
            $(ev.currentTarget).val(sanitizedValue);
        }
        
        if (sanitizedValue && sanitizedValue !== '') {
            this._generateFamilyRows(parseInt(sanitizedValue));
        } else {
            this._clearFamilyTable();
            this._generateInitialRow();
        }
    },