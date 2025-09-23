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


    _onMembersCountChange: function(ev) {
        var applicationState = this.$('input[name="application_state"]').val() || 
                            this.$('select[name="application_state"]').val() ||
                            this.$('.application_state').val();
        
        if (this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit')) {
            return;
        }
        
        var value = $(ev.currentTarget).val();
        var membersCount = parseInt(value);
        
        if (!isNaN(membersCount) && membersCount >= 1 && membersCount <= 8) {
            this._generateFamilyRows(membersCount);
        } else {
            this._clearFamilyTable();
            this._generateInitialRow();
        }
    },

   _clearFamilyTable: function() {
        $('#family-table-body').empty();
        $('#overseas-family-table-body').empty();
    },

    _generateFamilyRows: function(count) {
    var self = this;
    var citizenship = $('select[name="citizenship"]').val();
    
    var isOverseas = false;
    if (citizenship === 'Overseas') {
        isOverseas = true;
    } else if (!citizenship && window.location.href.includes('overseas')) {
        isOverseas = true;
    }
    
    var $tableBody = isOverseas ? $('#overseas-family-table-body') : $('#family-table-body');
    
    if ($tableBody.length === 0) {
        return;
    }
    
    var existingRowsCount = $tableBody.find('tr').length;
    
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    var isReadonly = this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit');
    
    if (isReadonly && existingRowsCount > 0) {
        return;
    }
    
    if (!isReadonly) {
        this._clearFamilyTable();
    }
    
    var applicantName = $('input[name="name"]').val() || '';
    var applicantBloodGroup = $('select[name="blood_group"]').val() || '';
    var applicantMobile = $('input[name="mobile"]').val() || '';
    var applicantEmergencyContact = $('input[name="emergency_contact"]').val() || '';
    
    var bloodGroupOptions = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB-', 'AB+'];
    var relationOptions = [
        'Father', 'Mother', 'Husband', 'Wife', 'Brother', 'Sister', 
        'Son', 'Daughter', 'Grandfather', 'Grandmother', 
        'Father-in-law', 'Mother-in-law', 'Brother-in-law', 'Sister-in-law', 
        'Son-in-law', 'Daughter-in-law', 'Spouse', 'Other'
    ];
    
    var existingFamilyData = this._getExistingFamilyData();
    var preservedFamilyData = $('input[name="preserved_family_data"]').val();
    var familyDataToUse = null;
    
    if (preservedFamilyData) {
        try {
            familyDataToUse = JSON.parse(preservedFamilyData);
        } catch (e) {
            console.log('Error parsing preserved family data:', e);
        }
    } else if (existingFamilyData) {
        familyDataToUse = existingFamilyData;
    }
    
    var actualCount = Math.max(count, familyDataToUse ? familyDataToUse.length : 1);
    
    for (var i = 0; i < actualCount; i++) {
        var rowHtml = '<tr id="family-row-' + i + '">';
        
        var nameValue = '';
        var relationValue = '';
        var bloodGroupValue = '';
        var mobileValue = '';
        var emergencyContactValue = '';
        
        if (familyDataToUse && familyDataToUse[i]) {
            nameValue = familyDataToUse[i].name || '';
            relationValue = familyDataToUse[i].relation || '';
            bloodGroupValue = familyDataToUse[i].blood_group || '';
            
            if (isOverseas) {
                mobileValue = familyDataToUse[i].mobile_number || '';
                emergencyContactValue = familyDataToUse[i].emergency_contact || '';
            } else {
                mobileValue = familyDataToUse[i].mobile || '';
                emergencyContactValue = familyDataToUse[i].emergency_contact || '';
            }
        } else if (i === 0) {
            nameValue = applicantName;
            relationValue = 'Head';
            bloodGroupValue = applicantBloodGroup;
            mobileValue = applicantMobile;
            emergencyContactValue = applicantEmergencyContact;
        }
        
        var nameReadonly = isReadonly ? ' readonly disabled style="background-color: #e9ecef; color: #6c757d;"' : '';
        var selectReadonly = isReadonly ? ' disabled style="pointer-events: none; background-color: #e9ecef; color: #6c757d; opacity: 1;"' : '';
        var fileDisabled = isReadonly ? ' disabled style="display:none;"' : '';
        
        rowHtml += '<td><input type="text" class="form-control" name="family_member_name_' + i + '" placeholder="Enter Name" value="' + nameValue + '"' + nameReadonly + ' /></td>';
        
        if (i === 0) {
            rowHtml += '<td><select class="form-control" name="family_member_relation_' + i + '"' + selectReadonly + '><option value="Head" selected>Head</option></select></td>';
        } else {
            rowHtml += '<td><select class="form-control" name="family_member_relation_' + i + '"' + selectReadonly + '><option value="">Select Relation</option>';
            relationOptions.forEach(function(relation) {
                var selected = (relation === relationValue) ? ' selected' : '';
                rowHtml += '<option value="' + relation + '"' + selected + '>' + relation + '</option>';
            });
            rowHtml += '</select></td>';
        }
        
        rowHtml += '<td><select class="form-control" name="family_member_blood_group_' + i + '"' + selectReadonly + '><option value="">Select...</option>';
        bloodGroupOptions.forEach(function(bloodGroup) {
            var selected = (bloodGroup === bloodGroupValue) ? ' selected' : '';
            rowHtml += '<option value="' + bloodGroup + '"' + selected + '>' + bloodGroup + '</option>';
        });
        rowHtml += '</select></td>';
        
        if (isOverseas) {
            rowHtml += '<td><input type="text" class="form-control" name="family_member_mobile_number_' + i + '" placeholder="Mobile Number" value="' + mobileValue + '"' + nameReadonly + ' /></td>';
            rowHtml += '<td><input type="text" class="form-control" name="family_member_emergency_contact_' + i + '" placeholder="Emergency Contact" value="' + emergencyContactValue + '"' + nameReadonly + ' /></td>';
            rowHtml += '<td><input type="file" class="form-control" name="family_member_passport_photo_' + i + '" accept="image/jpeg,image/jpg"' + fileDisabled + ' /></td>';
        } else {
            rowHtml += '<td><input type="text" class="form-control" name="family_member_mobile_' + i + '" placeholder="Mobile Number" value="' + mobileValue + '"' + nameReadonly + ' /></td>';
            rowHtml += '<td><input type="text" class="form-control" name="family_member_emergency_contact_' + i + '" placeholder="Emergency Contact" value="' + emergencyContactValue + '"' + nameReadonly + ' /></td>';
            rowHtml += '<td><input type="file" class="form-control" name="family_member_passport_photo_' + i + '" accept="image/jpeg,image/jpg"' + fileDisabled + ' /></td>';
        }
        
        rowHtml += '</tr>';
        
        $tableBody.append(rowHtml);
    }
    
    if (!familyDataToUse && !isReadonly) {
        this._syncApplicantData();
    }
},
    _getExistingFamilyData: function() {
        var familyDataInput = $('input[name="existing_family_data"]');
        if (familyDataInput.length && familyDataInput.val()) {
            try {
                return JSON.parse(familyDataInput.val());
            } catch (e) {
                console.log('Error parsing existing family data:', e);
            }
        }
        return null;
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
       
       $('#has_voter_id_in_kanha_field').removeAttr('required');
       $('#voter_id_number_optional_field').removeAttr('required');
       $('#wants_to_apply_voter_id_field').removeAttr('required');
       $('#members_count_id').removeAttr('required');
       $("label[for='has_voter_id_in_kanha'] .s_website_form_mark").remove();
       $("label[for='voter_id_number_optional'] .s_website_form_mark").remove();
       $("label[for='wants_to_apply_voter_id'] .s_website_form_mark").remove();
       
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
       
       $('#residence_type_select').attr('required', true);
       $("label[for='residence_type'] .s_website_form_mark").remove();
       $("label[for='residence_type']").append('<span class="s_website_form_mark"> *</span>');
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
       
       $('#has_voter_id_in_kanha_field').attr('required', true);
       $('#members_count_id').attr('required', true);
       $("label[for='has_voter_id_in_kanha'] .s_website_form_mark").remove();
       $("label[for='has_voter_id_in_kanha']").append('<span class="s_website_form_mark"> *</span>');
       
       var hasVoterIdValue = this.$('select[name="has_voter_id_in_kanha"]').val();
       if (hasVoterIdValue === 'Yes') {
           $('input[name="voter_id_number_optional"]').attr('required', true);
           $("label[for='voter_id_number_optional'] .s_website_form_mark").remove();
           $("label[for='voter_id_number_optional']").append('<span class="s_website_form_mark"> *</span>');
       } else if (hasVoterIdValue === 'No') {
           $('select[name="wants_to_apply_voter_id"]').attr('required', true);
           $("label[for='wants_to_apply_voter_id'] .s_website_form_mark").remove();
           $("label[for='wants_to_apply_voter_id']").append('<span class="s_website_form_mark"> *</span>');
       }
       
       $('#tab-kanha_voter_id').removeClass('d-none');
       $('#pane-kanha_voter_id').removeClass('d-none');
       
       $('#birth_country_id_field').attr('required', true);
       $('#already_have_kanha_voter_id_field').attr('required', true);
       
       $('#residence_type_select').attr('required', true);
       $("label[for='residence_type'] .s_website_form_mark").remove();
       $("label[for='residence_type']").append('<span class="s_website_form_mark"> *</span>');
   }
   
   this._generateInitialRow();
},

    _syncApplicantData: function() {
        var self = this;
        var citizenship = $('select[name="citizenship"]').val() || 'Indian';
        var isOverseas = (citizenship === 'Overseas');
        
        if (this.isFormSaved) {
            return;
        }
        
        $('input[name="name"]').off('input.familySync').on('input.familySync', function() {
            $('input[name="family_member_name_0"]').val($(this).val());
        });
        
        $('select[name="blood_group"]').off('change.familySync').on('change.familySync', function() {
            $('select[name="family_member_blood_group_0"]').val($(this).val());
        });
        
        if (isOverseas) {
            $('input[name="emergency_contact"]').off('input.familySync').on('input.familySync', function() {
                var emergencyContactValue = $(this).val();
                $('input[name="family_member_emergency_contact_0"]').val(emergencyContactValue);
            });
        }
        
        var currentName = $('input[name="name"]').val();
        var currentBloodGroup = $('select[name="blood_group"]').val();
        var currentEmergencyContact = '';
        
        if (isOverseas) {
            currentEmergencyContact = $('input[name="emergency_contact"]').val() || '';
        }
        
        if (currentName) {
            $('input[name="family_member_name_0"]').val(currentName);
        }
        if (currentBloodGroup) {
            $('select[name="family_member_blood_group_0"]').val(currentBloodGroup);
        }
        if (isOverseas && currentEmergencyContact) {
            $('input[name="family_member_emergency_contact_0"]').val(currentEmergencyContact);
        }
    },

    _removeRequiredFields: function() {
        $('#year_of_birth_field').removeAttr('required');
        $('#birth_state_id_field').removeAttr('required');
        $('#birth_district_field').removeAttr('required');
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
        var applicationState = this.$('input[name="application_state"]').val() || 
                            this.$('select[name="application_state"]').val() ||
                            this.$('.application_state').val();
        
        if (this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit')) {
            ev.preventDefault();
            return false;
        }
    },

    
    _restrictSpecialCharacter: function(e) {  
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

    _onHasVoterIdChange: function (ev) {
    var selectedValue = this.$('select[name="has_voter_id_in_kanha"]').val();
    var citizenship = this.$('select[name="citizenship"]').val();
    
    if (selectedValue === 'Yes') {
        $('.voter_id_number_optional_field').removeClass('d-none');
        $('.wants_to_apply_voter_id_field').addClass('d-none');
        
        if (citizenship === 'Indian' || !citizenship) {
            $('input[name="voter_id_number_optional"]').attr('required', true);
            $("label[for='voter_id_number_optional'] .s_website_form_mark").remove();
            $("label[for='voter_id_number_optional']").append('<span class="s_website_form_mark"> *</span>');
        }
        
        $('select[name="wants_to_apply_voter_id"]').removeAttr('required');
        $("label[for='wants_to_apply_voter_id'] .s_website_form_mark").remove();
        
    } else if (selectedValue === 'No') {
        $('.voter_id_number_optional_field').addClass('d-none');
        $('.wants_to_apply_voter_id_field').removeClass('d-none');
        
        if (citizenship === 'Indian' || !citizenship) {
            $('select[name="wants_to_apply_voter_id"]').attr('required', true);
            $("label[for='wants_to_apply_voter_id'] .s_website_form_mark").remove();
            $("label[for='wants_to_apply_voter_id']").append('<span class="s_website_form_mark"> *</span>');
        }
        
        $('input[name="voter_id_number_optional"]').removeAttr('required');
        $("label[for='voter_id_number_optional'] .s_website_form_mark").remove();
        
    } else {
        $('.voter_id_number_optional_field').addClass('d-none');
        $('.wants_to_apply_voter_id_field').addClass('d-none');
        $('input[name="voter_id_number_optional"]').removeAttr('required');
        $('select[name="wants_to_apply_voter_id"]').removeAttr('required');
        $("label[for='voter_id_number_optional'] .s_website_form_mark").remove();
        $("label[for='wants_to_apply_voter_id'] .s_website_form_mark").remove();
    }
},

    _preserveVoterIdData: function() {
    var hasVoterIdValue = this.$('select[name="has_voter_id_in_kanha"]').val();
    var voterIdNumber = this.$('input[name="voter_id_number_optional"]').val();
    var wantsToApply = this.$('select[name="wants_to_apply_voter_id"]').val();
    
    $('input[name="has_voter_id_preserved"]').remove();
    $('input[name="wants_to_apply_preserved"]').remove();
    
    if (hasVoterIdValue) {
        $('<input type="hidden" name="has_voter_id_preserved">').val(hasVoterIdValue).appendTo('form');
    }
    
    if (voterIdNumber && hasVoterIdValue === 'Yes') {
        $('#voter_id_number_optional_id').val(voterIdNumber);
    }
    
    if (wantsToApply && hasVoterIdValue === 'No') {
        $('<input type="hidden" name="wants_to_apply_preserved">').val(wantsToApply).appendTo('form');
    }
},

_restoreVoterIdData: function() {
    var preservedHasVoterId = $('input[name="has_voter_id_preserved"]').val();
    var preservedVoterIdNumber = $('#voter_id_number_optional_id').val();
    var preservedWantsToApply = $('input[name="wants_to_apply_preserved"]').val();
    
    if (preservedHasVoterId) {
        this.$('select[name="has_voter_id_in_kanha"]').val(preservedHasVoterId);
        this.$('select[name="has_voter_id_in_kanha"]').trigger('change');
        
        setTimeout(() => {
            if (preservedVoterIdNumber && preservedHasVoterId === 'Yes') {
                this.$('input[name="voter_id_number_optional"]').val(preservedVoterIdNumber);
            }
            
            if (preservedWantsToApply && preservedHasVoterId === 'No') {
                this.$('select[name="wants_to_apply_voter_id"]').val(preservedWantsToApply);
            }
        }, 100);
    }
},

    _preserveFamilyData: function() {
    var citizenship = $('select[name="citizenship"]').val();
    var isOverseas = (citizenship === 'Overseas');
    var $tableBody = isOverseas ? $('#overseas-family-table-body') : $('#family-table-body');
    var familyData = [];
    
    $tableBody.find('tr').each(function(index) {
        var $row = $(this);
        var familyMember = {
            'name': $row.find('input[name="family_member_name_' + index + '"]').val() || '',
            'relation': $row.find('select[name="family_member_relation_' + index + '"]').val() || '',
            'blood_group': $row.find('select[name="family_member_blood_group_' + index + '"]').val() || ''
        };
        
        if (isOverseas) {
            familyMember['emergency_contact'] = $row.find('input[name="family_member_emergency_contact_' + index + '"]').val() || '';
        }
        
        if (familyMember.name || familyMember.relation || familyMember.blood_group) {
            familyData.push(familyMember);
        }
    });
    
    $('input[name="preserved_family_data"]').remove();
    $('<input type="hidden" name="preserved_family_data" value="' + JSON.stringify(familyData) + '">').appendTo('form');
    
    var membersCount = $('#members_count_id').val();
    if (membersCount) {
        $('input[name="preserved_members_count"]').remove();
        $('<input type="hidden" name="preserved_members_count" value="' + membersCount + '">').appendTo('form');
    }
},
    _restoreFamilyData: function() {
    var preservedFamilyData = $('input[name="preserved_family_data"]').val();
    var existingFamilyData = $('input[name="existing_family_data"]').val();
    var preservedMembersCount = $('input[name="preserved_members_count"]').val();
    
    var familyDataToUse = preservedFamilyData || existingFamilyData;
    
    if (preservedMembersCount) {
        $('#members_count_id').val(preservedMembersCount);
    }
    
    if (familyDataToUse) {
        try {
            var familyData = JSON.parse(familyDataToUse);
            var citizenship = $('select[name="citizenship"]').val();
            var isOverseas = (citizenship === 'Overseas');
            var $tableBody = isOverseas ? $('#overseas-family-table-body') : $('#family-table-body');
            
            if ($tableBody.length === 0) {
                return;
            }
            
            var applicationState = this.$('input[name="application_state"]').val() || 
                                this.$('select[name="application_state"]').val() ||
                                this.$('.application_state').val();
            
            var isReadonly = this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit');
            
            if (!isReadonly) {
                $tableBody.empty();
            }
            
            var bloodGroupOptions = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB-', 'AB+'];
            var relationOptions = [
                'Father', 'Mother', 'Husband', 'Wife', 'Brother', 'Sister', 
                'Son', 'Daughter', 'Grandfather', 'Grandmother', 
                'Father-in-law', 'Mother-in-law', 'Brother-in-law', 'Sister-in-law', 
                'Son-in-law', 'Daughter-in-law', 'Spouse', 'Other'
            ];
            
            familyData.forEach(function(member, index) {
                var rowHtml = '<tr id="family-row-' + index + '">';
                
                var nameReadonly = isReadonly ? ' readonly disabled style="background-color: #e9ecef; color: #6c757d;"' : '';
                var selectReadonly = isReadonly ? ' disabled style="pointer-events: none; background-color: #e9ecef; color: #6c757d; opacity: 1;"' : '';
                
                rowHtml += '<td><input type="text" class="form-control" name="family_member_name_' + index + '" value="' + (member.name || '') + '"' + nameReadonly + ' /></td>';
                
                if (index === 0) {
                    rowHtml += '<td><select class="form-control" name="family_member_relation_' + index + '"' + selectReadonly + '><option value="Head" selected>Head</option></select></td>';
                } else {
                    rowHtml += '<td><select class="form-control" name="family_member_relation_' + index + '"' + selectReadonly + '><option value="">Select Relation</option>';
                    relationOptions.forEach(function(relation) {
                        var selected = (relation === member.relation) ? ' selected' : '';
                        rowHtml += '<option value="' + relation + '"' + selected + '>' + relation + '</option>';
                    });
                    rowHtml += '</select></td>';
                }
                
                rowHtml += '<td><select class="form-control" name="family_member_blood_group_' + index + '"' + selectReadonly + '><option value="">Select...</option>';
                bloodGroupOptions.forEach(function(bloodGroup) {
                    var selected = (bloodGroup === member.blood_group) ? ' selected' : '';
                    rowHtml += '<option value="' + bloodGroup + '"' + selected + '>' + bloodGroup + '</option>';
                });
                rowHtml += '</select></td>';
                
                if (isOverseas) {
                    rowHtml += '<td><input type="text" class="form-control" name="family_member_mobile_number_' + index + '" value="' + (member.mobile_number || '') + '"' + nameReadonly + ' /></td>';
                    rowHtml += '<td><input type="text" class="form-control" name="family_member_emergency_contact_' + index + '" value="' + (member.emergency_contact || '') + '"' + nameReadonly + ' /></td>';
                    var fileDisabled = isReadonly ? ' disabled style="display:none;"' : '';
                    rowHtml += '<td><input type="file" class="form-control" name="family_member_passport_photo_' + index + '" accept="image/jpeg,image/jpg"' + fileDisabled + ' /></td>';
                } else {
                    rowHtml += '<td><input type="text" class="form-control" name="family_member_mobile_' + index + '" value="' + (member.mobile || '') + '"' + nameReadonly + ' /></td>';
                    rowHtml += '<td><input type="text" class="form-control" name="family_member_emergency_contact_' + index + '" value="' + (member.emergency_contact || '') + '"' + nameReadonly + ' /></td>';
                    var fileDisabled = isReadonly ? ' disabled style="display:none;"' : '';
                    rowHtml += '<td><input type="file" class="form-control" name="family_member_passport_photo_' + index + '" accept="image/jpeg,image/jpg"' + fileDisabled + ' /></td>';
                }
                
                rowHtml += '</tr>';
                $tableBody.append(rowHtml);
            });
        } catch (e) {
            console.log('Error parsing family data:', e);
        }
    }
},

    _restoreSettings: function () {
        var selectedValue = this.$('select[name="has_voter_id_in_kanha"]').val();
        var citizenship = this.$('select[name="citizenship"]').val();
        
        if (selectedValue === 'Yes') {
            $('.voter_id_number_optional_field').removeClass('d-none');
            $('.wants_to_apply_voter_id_field').addClass('d-none');
            if (citizenship === 'Indian' || !citizenship) {
                $('input[name="voter_id_number_optional"]').attr('required', true);
                $("label[for='voter_id_number_optional'] .s_website_form_mark").remove();
                $("label[for='voter_id_number_optional']").append('<span class="s_website_form_mark"> *</span>');
            }
        } else if (selectedValue === 'No') {
            $('.voter_id_number_optional_field').addClass('d-none');
            $('.wants_to_apply_voter_id_field').removeClass('d-none');
            if (citizenship === 'Indian' || !citizenship) {
                $('select[name="wants_to_apply_voter_id"]').attr('required', true);
                $("label[for='wants_to_apply_voter_id'] .s_website_form_mark").remove();
                $("label[for='wants_to_apply_voter_id']").append('<span class="s_website_form_mark"> *</span>');
            }
        } else {
            $('.voter_id_number_optional_field').addClass('d-none');
            $('.wants_to_apply_voter_id_field').addClass('d-none');
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

    _onBrowseFile: function (ev) {
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    if (this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit')) {
        ev.preventDefault();
        return false;
    }
    
    ev.preventDefault();
    var fileupload = $(ev.target).attr('fileupload');
    if (fileupload) {
        $(ev.currentTarget).closest('form').find('.' + fileupload).trigger('click');
    }
},

    _onClearFile: function (ev) {
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    if (this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit')) {
        ev.preventDefault();
        return false;
    }
    
    ev.preventDefault();
    var fileupload_input = $(ev.target).attr('fileupload_input');
    var filename_input = $(ev.target).attr('filename_input');
    var $form = $(ev.currentTarget).closest('form');
    
    if (filename_input) {
        $form.find('.' + filename_input).val('');
    }
    if (fileupload_input) {
        $form.find('.' + fileupload_input).val('');
    }
},


    _onUploadPassportFrontImage: function (ev) {
        if (this.isFormSaved) {
            ev.preventDefault();
            return;
        }
        
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
                ev.target.value = "";
                var $form = $(ev.currentTarget).closest('form');
                var filename_input = $(ev.target).attr('filename_input');
                $form.find('.'+filename_input).val('');
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
            ev.target.value = "";
        }
    },

    _onUploadPassportBackImage: function (ev) {
        if (this.isFormSaved) {
            ev.preventDefault();
            return;
        }
        
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
                ev.target.value = "";
                var $form = $(ev.currentTarget).closest('form');
                var filename_input = $(ev.target).attr('filename_input');
                $form.find('.'+filename_input).val('');
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
            ev.target.value = "";
        }
    },

    _onUploadIndianVisa: function (ev) {
        if (this.isFormSaved) {
            ev.preventDefault();
            return;
        }
        
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
                ev.target.value = "";
                var $form = $(ev.currentTarget).closest('form');
                var filename_input = $(ev.target).attr('filename_input');
                $form.find('.'+filename_input).val('');
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
            ev.target.value = "";
        }
    },
    
    _onUploadPassportPhoto: function (ev) {
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

    _onUploadKanhaVoterIdImage: function (ev) {
        if (this.isFormSaved) {
            ev.preventDefault();
            return;
        }
        
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
                ev.target.value = "";
                var $form = $(ev.currentTarget).closest('form');
                var filename_input = $(ev.target).attr('filename_input');
                $form.find('.'+filename_input).val('');
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
            ev.target.value = "";
        }
    },
    
    _onUploadKanhaVoterIdBackImage: function (ev) {
        if (this.isFormSaved) {
            ev.preventDefault();
            return;
        }
        
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
                ev.target.value = "";
                var $form = $(ev.currentTarget).closest('form');
                var filename_input = $(ev.target).attr('filename_input');
                $form.find('.'+filename_input).val('');
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
            ev.target.value = "";
        }
    },

    _onFileUploadChange: function (ev) {
        if (this.isFormSaved) {
            ev.preventDefault();
            return;
        }
        
        if (!ev.currentTarget.files.length) {
            return;
        }
        var file_name = ev.target.files[0].name
        var $form = $(ev.currentTarget).closest('form');
        var filename_input = $(ev.target).attr('filename_input')
        $form.find('.'+filename_input).val(file_name);
    },

    _onUploadAgeProof: function (ev) {
        if (this.isFormSaved) {
            ev.preventDefault();
            return;
        }
        
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
                ev.target.value = "";
                var $form = $(ev.currentTarget).closest('form');
                var filename_input = $(ev.target).attr('filename_input');
                $form.find('.'+filename_input).val('');
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
            ev.target.value = "";
        }
    },

    _onUploadAddressProof: function (ev) {
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
        var $form = $(ev.currentTarget).closest('form');
        var filename_input = $(ev.target).attr('filename_input');
        if (filename_input) {
            $form.find('.' + filename_input).val('');
        }
        return;
    }
    
    var fileSize = file.size / 1024;
    if (fileSize > 500) {
        var fileSizeFormatted = fileSize.toFixed(2);
        Dialog.alert(null, "File is too big. Your File size is " + fileSizeFormatted + "KB. File size cannot exceed 500KB.");
        ev.target.value = "";
        var $form = $(ev.currentTarget).closest('form');
        var filename_input = $(ev.target).attr('filename_input');
        if (filename_input) {
            $form.find('.' + filename_input).val('');
        }
    }
    else{
        var file_name = ev.target.files[0].name;
        var $form = $(ev.currentTarget).closest('form');
        var filename_input = $(ev.target).attr('filename_input');
        if (filename_input) {
            $form.find('.' + filename_input).val(file_name);
        }
    }
},
    _onUploadAdharFrontImage: function (ev) {
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

    _onUploadAdharBackImage: function (ev) {
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
                $('#birth_state_textfield_id').attr('required', false);
                $('.birth_state_dropdown_field_div').removeClass('d-none');
                $('.birth_state_textfield_div').addClass('d-none');
            }
            else{
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

                var isValid = true;
                var errorMessages = [];

                if (!vehicle_number || vehicle_number.trim() === '') {
                    isValid = false;
                    errorMessages.push('Vehicle Number is required');
                    $modal.find('input[name="vehicle_number"]').addClass('is-invalid');
                } else {
                    $modal.find('input[name="vehicle_number"]').removeClass('is-invalid');
                }

                if (!vehicle_owner || vehicle_owner.trim() === '') {
                    isValid = false;
                    errorMessages.push('Vehicle Owner is required');
                    $modal.find('input[name="vehicle_owner"]').addClass('is-invalid');
                } else {
                    $modal.find('input[name="vehicle_owner"]').removeClass('is-invalid');
                }

                if (!vehicle_type || vehicle_type === '' || vehicle_type === 'Select...') {
                    isValid = false;
                    errorMessages.push('Vehicle Type is required');
                    $modal.find('select[name="vehicle_type"]').addClass('is-invalid');
                } else {
                    $modal.find('select[name="vehicle_type"]').removeClass('is-invalid');
                }

                if (!isValid) {
                    $(".save_vehicle_line").attr('disabled', false);
                    Dialog.alert(null, errorMessages.join(', '));
                    return false;
                }

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
    var self = this;
    
    $(".family_website_form_submit, .family_website_form_save").attr('disabled', true).addClass('disabled');
    $("#loading").removeClass('hide');

    this._preserveVoterIdData();
    this._preserveFamilyData();

    var $form = $(e.currentTarget).closest('form');
    var form_action = $form.attr('action');
    
    if (!form_action) {
        self.update_status('error', "Form action URL is missing.");
        self._enableButtons();
        $("#loading").addClass('hide');
        return;
    }

    var formData = new FormData();
    var excludedFields = ['csrf_token', 'request_token', '_token', 'authenticity_token'];

    $form.find('input:not([type="file"]), select, textarea').each(function() {
        var $input = $(this);
        var name = $input.attr('name');
        var value = $input.val();
        
        if (name && excludedFields.indexOf(name) === -1) {
            if ($input.attr('type') === 'checkbox') {
                if ($input.is(':checked')) {
                    formData.append(name, value || 'on');
                }
            } else if ($input.attr('type') === 'radio') {
                if ($input.is(':checked')) {
                    formData.append(name, value || '');
                }
            } else {
                formData.append(name, value || '');
            }
        }
    });

    $form.find('input[type="file"]').each(function() {
        var fileInput = this;
        var name = fileInput.name;
        
        if (name && fileInput.files && fileInput.files.length > 0) {
            var file = fileInput.files[0];
            if (file && file.size > 0) {
                try {
                    formData.append(name, file, file.name);
                } catch (error) {
                    console.error("File append error for " + name + ":", error);
                }
            }
        }
    });

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

    var family_details = {};
    var citizenship = $('select[name="citizenship"]').val();
    var isOverseas = (citizenship === 'Overseas');
    var $tableBody = isOverseas ? $('#overseas-family-table-body') : $('#family-table-body');

    $tableBody.find('tr').each(function(index) {
        var $row = $(this);
        var familyMember = {
            'name': $row.find('input[name="family_member_name_' + index + '"]').val() || '',
            'relation': $row.find('select[name="family_member_relation_' + index + '"]').val() || '',
            'blood_group': $row.find('select[name="family_member_blood_group_' + index + '"]').val() || ''
        };
        
        if (isOverseas) {
            familyMember['mobile_number'] = $row.find('input[name="family_member_mobile_number_' + index + '"]').val() || '';
            familyMember['emergency_contact'] = $row.find('input[name="family_member_emergency_contact_' + index + '"]').val() || '';
            
            var passportPhotoFile = $row.find('input[name="family_member_passport_photo_' + index + '"]')[0];
            if (passportPhotoFile && passportPhotoFile.files && passportPhotoFile.files.length > 0) {
                var file = passportPhotoFile.files[0];
                if (file && file.size > 0) {
                    try {
                        formData.append('family_member_passport_photo_' + index, file, file.name);
                    } catch (error) {
                        console.error("Family member file append error:", error);
                    }
                }
            }
        } else {
            familyMember['mobile'] = $row.find('input[name="family_member_mobile_' + index + '"]').val() || '';
            familyMember['emergency_contact'] = $row.find('input[name="family_member_emergency_contact_' + index + '"]').val() || '';
        }
        
        family_details[index] = familyMember;
    });

    formData.append('vehicle_details_ids', JSON.stringify(vehicle_details));
    formData.append('vehicle_new_lines', JSON.stringify(vehicle_new_lines));
    formData.append('family_details', JSON.stringify(family_details));
    formData.append('is_submit', is_submit ? 'true' : 'false');

    var birth_country = document.getElementById("birth_country_id_field");
    if (birth_country) {
        var selected_country = birth_country.options[birth_country.selectedIndex].text;
        if (selected_country.trim() === 'India') {
            formData.append('birth_state_textfield', '');
        }
    }

    var csrf_token = $('input[name="csrf_token"]').val() || $('meta[name="csrf-token"]').attr('content') || $('[name="csrf_token"]').val();
    if (csrf_token) {
        formData.append('csrf_token', csrf_token);
    }

    var final_url = form_action;
    if ($form.data('force_action')) {
        final_url += $form.data('force_action');
    } else if ($form.data('model_name')) {
        final_url += $form.data('model_name');
    }

    $.ajax({
        url: final_url,
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        timeout: 60000,
        success: function(response) {
            $("#loading").addClass('hide');
            self._enableButtons();
            
            try {
                var result_data;
                if (typeof response === 'string') {
                    try {
                        result_data = JSON.parse(response);
                    } catch (parseError) {
                        if (response.includes('error') || response.includes('Error')) {
                            self.update_status('error', "Server returned an error. Please check your form data and try again.");
                            return;
                        }
                        result_data = {id: true, status: 'success'};
                    }
                } else {
                    result_data = response;
                }

                if (result_data.error || (!result_data.id && result_data.status !== 'success')) {
                    var errorMessage = result_data.error_message || result_data.message || "Form submission failed. Please check all required fields and try again.";
                    self.update_status('error', errorMessage);

                    if (result_data.error_fields) {
                        self.check_error_fields_save(Object.keys(result_data.error_fields));
                        $("html, body").animate({ scrollTop: 0 }, "slow");
                    }
                    
                    self._restoreVoterIdData();
                    self._restoreFamilyData();
                } else {
                    self.isFormSaved = true;
                    
                    if (is_submit || result_data.status === 'submitted') {
                        self._makeFormReadonly();
                        self._hideAllFileUploads();
                        self._disableAllFileUploads();
                    } else {
                        self._restoreVoterIdData();
                        self._restoreFamilyData();
                    }
                    
                    var successMode = $form[0].dataset.successMode || ($form.attr('data-success_page') ? 'redirect' : 'nothing');
                    var successPage = $form[0].dataset.successPage || $form.attr('data-success_page');

                    switch (successMode) {
                        case 'redirect':
                            if (successPage) {
                                if (successPage.charAt(0) === "#") {
                                    $('html, body').animate({
                                        scrollTop: $(successPage).offset().top
                                    }, 500);
                                } else {
                                    window.location.href = is_submit ? successPage : "/family/";
                                }
                            } else {
                                window.location.href = "/family/";
                            }
                            break;

                        case 'message':
                            self.$target.addClass('d-none');
                            self.$target.parent().find('.s_website_form_end_message').removeClass('d-none');
                            break;

                        default:
                            var successMsg = is_submit ? "Form submitted successfully!" : "Form saved successfully!";
                            self.update_status('success', successMsg);
                            break;
                    }
                }
            } catch (parseError) {
                console.error("Response parsing error:", parseError);
                self.update_status('error', "Server response error. Please try again.");
                self._restoreVoterIdData();
                self._restoreFamilyData();
            }
        },
        error: function(xhr, status, error) {
            $("#loading").addClass('hide');
            self._enableButtons();
            
            var errorMessage = "Network error occurred. Please check your connection and try again.";
            if (xhr.status === 413) {
                errorMessage = "File size too large. Please reduce file sizes and try again.";
            } else if (xhr.status === 400) {
                errorMessage = "Invalid form data. Please check all fields and try again.";
            } else if (xhr.status === 500) {
                errorMessage = "Server error. Please try again later.";
            }
            
            console.error("Form submission error:", status, error);
            self.update_status('error', errorMessage);
            
            self._restoreVoterIdData();
            self._restoreFamilyData();
        }
    });
},
    _extractFilesData: function(formData) {
    var filesData = {};
    for (var pair of formData.entries()) {
        if (pair[1] instanceof File) {
            filesData[pair[0]] = {
                name: pair[1].name,
                size: pair[1].size,
                type: pair[1].type
            };
        }
    }
    return filesData;
},

    
    _enableButtons: function() {
        this.$target.find('.family_website_form_submit, .family_website_form_save')
            .removeAttr('disabled')
            .removeClass('disabled');
    },
    
    _validateForm: function (e) {
        e.preventDefault();
        
        var self = this;
        this.$target.find('.family_website_form_result').html('');
        var validation_result = self.check_error_fields({});
        var is_form_valid = Object.keys(validation_result)[0] === 'true';
        
        if (!is_form_valid) {
            var missing_fields = Object.values(validation_result)[0] || [];
            self.update_status('error', _t("Please fill in the form correctly. Missing fields: ") + missing_fields.join(', '));
            $("html, body").animate({ scrollTop: 0 }, "slow");
            return false;
        }
        return true;
    },

    _clearFormStatus: function (e) {
        this.$('#form_result_error').addClass('d-none');
        this.$('#form_result_success').addClass('d-none');
        
        this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { 
            var $field = $(field);
            $field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
        });
    },
    
    _onClickSave: function (e, is_submit=false) {
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    if (this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit')) {
        return;
    }
    
    this._clearFormStatus(e);
    var citizenship = $('.citizenship').val();
    var passport_number = $('#passport_number_input').val();
    var residence_type = $('select[name="residence_type"]').val();
    
    var self = this;
    var form_valid = true;
    var missing_fields = [];
    
    this.$target.find('.form-field, .s_website_form_field').each(function (k, field) {
        var $field = $(field);
        var field_name = $field.find('.col-form-label').attr('for') || $field.find('label').text().replace('*', '').trim();
        
        if ($field.hasClass('d-none') || $field.is(':hidden') || !$field.is(':visible')) {
            return;
        }
        
        var inputs = $field.find('.s_website_form_input, .o_website_form_input, input, select, textarea').not('#editable_select');
        var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
            if (input.name === 'year_of_birth' || input.name === 'birth_state_id' || input.name === 'birth_district') {
                return false;
            }
            
            var $input = $(input);
            if ($input.closest('.form-field, .s_website_form_field').hasClass('d-none') || 
                $input.closest('.form-field, .s_website_form_field').is(':hidden') ||
                !$input.closest('.form-field, .s_website_form_field').is(':visible') ||
                $input.hasClass('d-none') || $input.is(':hidden') || !$input.is(':visible')) {
                return false;
            }
            
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
            return input.required && !input.checkValidity();
        });
        
        $field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
        
        if (invalid_inputs.length) {
            if(field_name && field_name !== 'Year Of Birth' && field_name !== 'Birth State' && field_name !== 'Birth District') {
                missing_fields.push(field_name);
            }
            if(field_name !== 'Year Of Birth' && field_name !== 'Birth State' && field_name !== 'Birth District') {
                $field.addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                form_valid = false;
            }
        }
    });
    
    if(citizenship == 'Overseas' && !passport_number && $('#passport_number_input').is(':visible')){
        $('#passport_number_input').addClass('is-invalid');
        missing_fields.push('Passport Number');
        form_valid = false;
    }
    
    if((!residence_type || residence_type === '' || residence_type === 'Select...') && 
       $('select[name="residence_type"]').is(':visible')){
        $('select[name="residence_type"]').addClass('is-invalid');
        missing_fields.push('Residence Type');
        form_valid = false;
    }
    
    var family_validation_result = this._validateFamilyDetails();
    if (!family_validation_result.valid) {
        form_valid = false;
        missing_fields = missing_fields.concat(family_validation_result.missing_fields);
    }
    
    if(!form_valid) {
        var errorMessage = _t("Please fill in all required fields: ") + missing_fields.join(', ');
        this.update_status('error', errorMessage);
        $("html, body").animate({ scrollTop: 0 }, "slow");
        return false;
    }
    
    this._onSaveForm(e, is_submit);
},
    _validateFamilyDetails: function() {
    var citizenship = $('select[name="citizenship"]').val();
    var isOverseas = (citizenship === 'Overseas');
    var $tableBody = isOverseas ? $('#overseas-family-table-body') : $('#family-table-body');
    var missing_fields = [];
    var valid = true;
    
    if ($tableBody.length === 0) {
        return {valid: true, missing_fields: []};
    }
    
    $tableBody.find('tr').each(function(index) {
        var $row = $(this);
        var nameInput = $row.find('input[name="family_member_name_' + index + '"]');
        var relationSelect = $row.find('select[name="family_member_relation_' + index + '"]');
        var bloodGroupSelect = $row.find('select[name="family_member_blood_group_' + index + '"]');
        
        var mobileInput, emergencyContactInput;
        if (isOverseas) {
            mobileInput = $row.find('input[name="family_member_mobile_number_' + index + '"]');
            emergencyContactInput = $row.find('input[name="family_member_emergency_contact_' + index + '"]');
        } else {
            mobileInput = $row.find('input[name="family_member_mobile_' + index + '"]');
            emergencyContactInput = $row.find('input[name="family_member_emergency_contact_' + index + '"]');
        }
        
        var passportPhotoInput = $row.find('input[name="family_member_passport_photo_' + index + '"]');
        
        nameInput.removeClass('is-invalid');
        relationSelect.removeClass('is-invalid');
        bloodGroupSelect.removeClass('is-invalid');
        if (mobileInput.length) mobileInput.removeClass('is-invalid');
        if (emergencyContactInput.length) emergencyContactInput.removeClass('is-invalid');
        if (passportPhotoInput.length) passportPhotoInput.removeClass('is-invalid');
        
        var nameValue = nameInput.val() || '';
        var relationValue = relationSelect.val() || '';
        var bloodGroupValue = bloodGroupSelect.val() || '';
        var mobileValue = mobileInput.length ? (mobileInput.val() || '') : '';
        var emergencyContactValue = emergencyContactInput.length ? (emergencyContactInput.val() || '') : '';
        
        if (!nameValue.trim()) {
            nameInput.addClass('is-invalid');
            missing_fields.push('Family Member Name (Row ' + (index + 1) + ')');
            valid = false;
        }
        
        if (index > 0 && !relationValue) {
            relationSelect.addClass('is-invalid');
            missing_fields.push('Family Member Relation (Row ' + (index + 1) + ')');
            valid = false;
        }
        
        if (!bloodGroupValue) {
            bloodGroupSelect.addClass('is-invalid');
            missing_fields.push('Family Member Blood Group (Row ' + (index + 1) + ')');
            valid = false;
        }
        
        if (isOverseas) {
            if (!mobileValue.trim()) {
                if (mobileInput.length) {
                    mobileInput.addClass('is-invalid');
                    missing_fields.push('Family Member Mobile Number (Row ' + (index + 1) + ')');
                    valid = false;
                }
            }
            
            if (!emergencyContactValue.trim()) {
                if (emergencyContactInput.length) {
                    emergencyContactInput.addClass('is-invalid');
                    missing_fields.push('Family Member Emergency Contact (Row ' + (index + 1) + ')');
                    valid = false;
                }
            }
        }
    });
    
    return {valid: valid, missing_fields: missing_fields};
},

    
    _onSubmitForm: function (e) {
    var applicationState = this.$('input[name="application_state"]').val() || 
                        this.$('select[name="application_state"]').val() ||
                        this.$('.application_state').val();
    
    if (this.isFormSaved && !(applicationState === 'draft' || applicationState === 'approved_for_edit')) {
        return;
    }
    
    e.preventDefault();
    this._clearFormStatus(e);
    
    var self = this;
    var form_valid = true;
    var missing_fields = [];
    
    this.$target.find('.form-field, .s_website_form_field').each(function (k, field) {
        var $field = $(field);
        var field_name = $field.find('.col-form-label').attr('for') || $field.find('label').text().replace('*', '').trim();
        
        if ($field.hasClass('d-none') || $field.is(':hidden') || !$field.is(':visible')) {
            return;
        }
        
        var inputs = $field.find('.s_website_form_input, .o_website_form_input, input, select, textarea').not('#editable_select');
        var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
            if (input.name === 'year_of_birth' || input.name === 'birth_state_id' || input.name === 'birth_district') {
                return false;
            }
            
            var $input = $(input);
            if ($input.closest('.form-field, .s_website_form_field').hasClass('d-none') || 
                $input.closest('.form-field, .s_website_form_field').is(':hidden') ||
                !$input.closest('.form-field, .s_website_form_field').is(':visible') ||
                $input.hasClass('d-none') || $input.is(':hidden') || !$input.is(':visible')) {
                return false;
            }
            
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
            return input.required && !input.checkValidity();
        });
        
        $field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
        
        if (invalid_inputs.length) {
            if(field_name && field_name !== 'Year Of Birth' && field_name !== 'Birth State' && field_name !== 'Birth District') {
                missing_fields.push(field_name);
            }
            if(field_name !== 'Year Of Birth' && field_name !== 'Birth State' && field_name !== 'Birth District') {
                $field.addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                form_valid = false;
            }
        }
    });
    
    var citizenship = $('.citizenship').val();
    var passport_number = $('#passport_number_input').val();
    var residence_type = $('select[name="residence_type"]').val();
    
    if(citizenship == 'Overseas' && !passport_number && $('#passport_number_input').is(':visible')){
        $('#passport_number_input').addClass('is-invalid');
        missing_fields.push('Passport Number');
        form_valid = false;
    }
    
    if((!residence_type || residence_type === '' || residence_type === 'Select...') && 
       $('select[name="residence_type"]').is(':visible')){
        $('select[name="residence_type"]').addClass('is-invalid');
        missing_fields.push('Residence Type');
        form_valid = false;
    }
    
    var family_validation_result = this._validateFamilyDetails();
    if (!family_validation_result.valid) {
        form_valid = false;
        missing_fields = missing_fields.concat(family_validation_result.missing_fields);
    }
    
    if(!form_valid) {
        var errorMessage = _t("Please fill in all required fields: ") + missing_fields.join(', ');
        this.update_status('error', errorMessage);
        $("html, body").animate({ scrollTop: 0 }, "slow");
        return false;
    }
    
    this._onSaveForm(e, true);
},

    check_error_fields_save: function (error_fields_keys) {
    for (let i = 0; i < error_fields_keys.length; i++) {
        if (error_fields_keys[i] !== 'year_of_birth' && error_fields_keys[i] !== 'birth_state_id' && error_fields_keys[i] !== 'birth_district') {
            $("input[name='"+error_fields_keys[i]+"'], select[name='"+error_fields_keys[i]+"']").addClass('is-invalid');
        }
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
            if (input.name === 'year_of_birth' || input.name === 'birth_state_id' || input.name === 'birth_district') {
                return false;
            }

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
            if(field_name != undefined && field_name !== 'year_of_birth' && field_name !== 'birth_state_id' && field_name !== 'birth_district'){
                missing_fields.push(field_name)
            }
            if(field_name !== 'year_of_birth' && field_name !== 'birth_state_id' && field_name !== 'birth_district') {
                $field.addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                
                if (_.isString(error_fields[field_name])) {
                    $field.popover({content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top'});
                    $field.data("bs.popover").config.content = error_fields[field_name];
                    $field.popover('show');
                }
                form_valid = false;
            }
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
        var abhyasi_id_field = $('.abhyasi_id_id_class');
        var abhyasi_id_input = $('#abhyasi_id_id');
        
        if(is_preceptor.val() == 'Yes'){
            abhyasi_id_field.removeClass('d-none');
            abhyasi_id_input.attr('required', true);
            
            var label = abhyasi_id_field.find('label[for="Abhyasi ID"]');
            label.find('.s_website_form_mark').remove();
            label.append('<span class="s_website_form_mark"> *</span>');
        }
        else if(is_preceptor.val() == 'No'){
            abhyasi_id_field.addClass('d-none');
            abhyasi_id_input.removeAttr('required');
            abhyasi_id_input.val('');
            
            var label = abhyasi_id_field.find('label[for="Abhyasi ID"]');
            label.find('.s_website_form_mark').remove();
        }
        else{
            abhyasi_id_field.addClass('d-none');
            abhyasi_id_input.removeAttr('required');
            abhyasi_id_input.val('');
            
            var label = abhyasi_id_field.find('label[for="Abhyasi ID"]');
            label.find('.s_website_form_mark').remove();
        }
    },

    update_status: function (status, message) {
        message = message || '';
        
        var $result = this.$target.find('.family_website_form_result');

        this.$target.find('#form_result_error').addClass('d-none');
        this.$target.find('#form_result_success').addClass('d-none');

        if (status === 'error') {
            this.$target.find('#form_result_error').removeClass('d-none');
            if (!message) {
                message = _t("An error has occurred, the form has not been sent.");
            }
        } else if (status === 'success') {
            this.$target.find('#form_result_success').removeClass('d-none');
        }

        $result.html(message);
    },
    
});

return publicWidget.registry.portalPartnerDetails;

});