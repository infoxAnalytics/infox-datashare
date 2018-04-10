Survey
    .StylesManager
    .applyTheme("darkblue");

var json = {
    pages: [
         {
            title: "PART ONE : Demographics and Professional Experience",
            questions: [
                {
                    type: "text",
                    name: "age",
                    title: "What is your age ?"
                    //visibleIf: "{gender} = 'many'"
                }, {
                    type: "radiogroup",
                    name: "gender",
                    title: "What is your gender ?",
                    isRequired: true,
                    choices: ["Male", "Female"],
                    hasOther: true,
                    otherText: "Other (please specify its name)",
                    otherErrorText: "Please enter your gender."
                }, {
                    type: "radiogroup",
                    name: "academicTitle",
                    title: "What is your current academic title ?",
                    isRequired: true,
                    choices: ["Resident", "Specialist/Consultant", "Assist/Assoc/Prof"],
                    hasOther: true,
                    otherText: "Other (please specify its name)",
                    otherErrorText: "Please enter your current academic title."
                }, {
                    type: "radiogroup",
                    name: "academicDegree",
                    title: "How long have you held your academic degree ?",
                    isRequired: true,
                    choices: ["One", "Two", "Three", "Four"],
                    hasOther: true,
                    otherText: "More (please specify its long)",
                    otherErrorText: "Please enter your long of academic degree."
                }, {
                    type: "checkbox",
                    name: "instType",
                    title: "Please select the type of your institution ? (You can select more than one)",
                    isRequired: true,
                    //visibleIf: "{academicDegree} = 'many' and {academicTitle} = 'all'",
                    choices: [
                    "Private hospital/clinic",
                    "Public hospital",
                    "University/educational hospital (private or public)"
                    ],
                    hasOther: true,
                    otherText: "Other (please state)",
                    otherErrorText: "Please enter the type of your institution."
                }
            ]
        }, {
            title: "PART TWO : Attitudes in Use Of Cellular Phone",
            questions: [
                {
                    type: "radiogroup",
                    name: "phone",
                    title: "Do you use a smartphone?",
                    isRequired: true,
                    choices: ["ok|Yes", "not|No"]
                }, {
                    type: "radiogroup",
                    name: "oprtSystem",
                    title: "Which operating system does your smartphone have?",
                    isRequired: true,
                    visibleIf: "{phone} = 'ok'",
                    choices: ["IOS", "Android"],
                    hasOther: true,
                    otherText: "Other (please specify its name)",
                    otherErrorText: "Please enter your operating system on your smartphone ."
                }, {
                    type: "checkbox",
                    name: "application",
                    title: "Which instant messaging application(s) do you use? (Please select all that apply)",
                    isRequired: true,
                    visibleIf: "{phone} = 'ok'",
                    choices: ["WhatsApp", "Telegram"],
                    hasOther: true,
                    otherText: "Other (please specify its name)",
                    otherErrorText: "Please enter your instant messaging application(s) you use."
                }, {
                    type: "radiogroup",
                    name: "socialMedia",
                    title: "Do you use social media applications (facebook, instagram, twitter etc.) on your smartphone for any purpose?",
                    isRequired: true,
                    visibleIf: "{phone} = 'ok'",
                    choices: ["Several times a day", "Several times a week", "Rarely", "Never"]
                }, {
                    type: "radiogroup",
                    name: "stolen",
                    title: "Is your cellular phone ever lost or stolen?",
                    isRequired: true,
                    visibleIf: "{phone} = 'ok'",
                    choices: ["Yes", "No"]
                }
            ]
        }, {
            title: "PART THREE : Comments on Smartphone Application Usage for Consultation",
            questions: [
                {
                    type: "radiogroup",
                    name: "share",
                    title: "Have you ever share, ask opinion or make comment about a case on social media applications?",
                    isRequired: true,
                    choices: ["Often", "Several times", "Less than three times", "Never"]
                }, {
                    type: "radiogroup",
                    name: "purpose",
                    title: "Do you know that instant messaging applications on smartphones are used for medical consultation purposes?",
                    isRequired: true,
                    choices: ["notend|Yes", "end|No"]
                }, {
                    type: "radiogroup",
                    name: "adequate",
                    title: "In general, do you think instant messaging applications are technically adequate for consultation purposes? (considering resolution, data transfer speed, universality...)",
                    isRequired: true,
                    visibleIf: "{purpose} = 'notend'",
                    choices: ["Extremely", "Very", "Moderately", "Slightly", "Not at all"]
                }, {
                    type: "radiogroup",
                    name: "diagnosis",
                    title: "Do you think that consulting a patient through instant messaging applications compromises the diagnosis?",
                    isRequired: true,
                    visibleIf: "{purpose} = 'notend'",
                    choices: ["Extremely", "Very", "Moderately", "Slightly", "Not at all"]
                }
            ]
        }, {
            title: "PART FOUR : Frequency of Instant Messaging Application Usage for Consultation",
            questions: [
                {
                    type: "radiogroup",
                    name: "inMsg",
                    title: "Do you use instant messaging applications for consultation purposes?",
                    isRequired: true,
                    choices: ["a|Everyday", "b|A few times a week", "c|Seldom", "d|Never"]
                }, {
                    type: "checkbox",
                    name: "formats",
                    title: "Which of the following formats do you use for consultation purposes in your messaging applications for your own patients? (Please select all that apply)",
                    isRequired: true,
                    visibleIf: "{inMsg} != 'd'",
                    choices: ["Text", "Image", "Video", "Voice message"],
                    hasOther: true,
                    otherText: "Other (please specify its name)",
                    otherErrorText: "Please enter your format."
                }, {
                    type: "checkbox",
                    name: "prefer",
                    title: "Why do you prefer instant messaging applications for consultation purposes? (Please select all that apply)",
                    isRequired: true,
                    visibleIf: "{inMsg} != 'd'",
                    choices: ["Fast", "Reliable", "Easier than using a monitor"],
                    hasOther: true,
                    otherText: "Other (please specify its name)",
                    otherErrorText: "Please enter your cause of your prefer."
                }, {
                    type: "radiogroup",
                    name: "distrust",
                    title: "Which of the following do you distrust most for consultation by instant messaging applications?",
                    isRequired: true,
                    visibleIf: "{inMsg} != 'd'",
                    choices: ["Text", "Image", "Video", "Voice message"],
                    hasOther: true,
                    otherText: "Other (please specify its name)",
                    otherErrorText: "Please enter your distrust most."
                }, {
                    type: "radiogroup",
                    name: "diagnosisSolely",
                    title: "Have you ever based your diagnosis solely on a media (image or video) received through instant messaging application without confirming with other systems?",
                    isRequired: true,
                    visibleIf: "{inMsg} != 'd'",
                    choices: ["Yes", "No"]
                }
            ]
        }, {
            title: "PART FIVE : Problems with Usage of Instant Messaging Application for Consultation",
            questions: [
                {
                    type: "radiogroup",
                    name: "identityPatients",
                    title: "Do you keep the identity of the patients confidential during sending/receiving the messages?",
                    isRequired: true,
                    choices: ["Text message", "Image", "Video", "Voice message"]
                }, {
                    type: "radiogroup",
                    name: "managePatients",
                    title: "How do you manage the patients information in your personal phone?",
                    isRequired: true,
                    choices: [
                    "I delete the confidential information as soon as I finish the consultation",
                    "I do not have any special attention for patient information",
                    "I keep it in my phone for any future legal problems"
                    ]
                }, {
                    type: "radiogroup",
                    name: "legalProblems",
                    title: "Do you think consultation via instant messaging applications can cause any legal problems?",
                    isRequired: true,
                    choices: ["Yes", "No", "No idea"]
                }, {
                    type: "radiogroup",
                    name: "hasRegulation",
                    title: "Does your institution, region or country has regulations for consultation via instant messaging applications?",
                    isRequired: true,
                    choices: ["Yes", "No", "No idea"]
                }, {
                    type: "radiogroup",
                    name: "anyExperience",
                    title: "Do you or any of your colleague had any experience of misdiagnosis on an instant message consultation ?",
                    isRequired: true,
                    choices: ["Many times", "Several times", "Once", "Not at all"]
                }, {
                    type: "radiogroup",
                    name: "creatingAppEx",
                    title: "Do you think creating an electronic platform or an application exclusively for consultation is necessary?",
                    isRequired: true,
                    choices: ["Yes", "No", "No idea"]
                }, {
                    type: "comment",
                    name: "whatFeatures",
                    title: "What features would this electronic platform or application for consultation should have?"
                }
            ]
        }
    ]
};

window.survey = new Survey.Model(json);

$("#surveyElement").Survey({
    model: survey,
    onComplete:sendDataToServer
});

function sendDataToServer(survey) {
  var data = {"PROCESS": "SaveSurvey", "DATA": JSON.stringify(survey.data)}
  // Ajax requester body
    $.ajax({
        type: 'POST',
        url: '/main-components',
        data: data,
        dataType: 'json',
        success: function(data) {
            if ( data.STATUS == "OK" ) {
                    new PNotify({
                    title: 'Completed',
                    text: data.MESSAGE,
                    type: 'success'
            });
            } else {
            new PNotify({
                    title: 'Oops !!! Something went wrong.',
                    text: data.ERROR,
                    type: 'error'
            });
            }
        }
    });
}