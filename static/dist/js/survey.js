Survey
    .StylesManager
    .applyTheme("darkblue");

var json = {
    pages: [
         {
            title: "Age information",
            questions: [
                {
                    type: "text",
                    name: "age",
                    title: "What is your age ?",
                    //visibleIf: "{gender} = 'many'"
                }
            ]
        },{
            title: "Specifying gender",
            questions: [
                {
                    type: "radiogroup",
                    name: "gender",
                    title: "What is your gender ?",
                    isRequired: true,
                    choices: ["Male", "Female"],
                    hasOther: true,
                    otherText: "Other (please specify its name)",
                    otherErrorText: "Please enter your gender."
                }
            ]
        },{
            title: "Academic Title",
            questions: [
                {
                    type: "radiogroup",
                    name: "academicTitle",
                    title: "What is your current academic title ?",
                    isRequired: true,
                    choices: ["Resident", "Specialist/Consultant", "Assist/Assoc/Prof"],
                    hasOther: true,
                    otherText: "Other (please specify its name)",
                    otherErrorText: "Please enter your current academic title."
                }
            ]
        },{
            title: "Academic Degree",
            questions: [
                {
                    type: "radiogroup",
                    name: "academicDegree",
                    title: "How long have you held your academic degree ?",
                    isRequired: true,
                    choices: ["One", "Two", "Three", "Four"],
                    hasOther: true,
                    otherText: "More (please specify its long)",
                    otherErrorText: "Please enter your long of academic degree."
                }
            ]
        },{
            title: "Type of Your Institution",
            questions: [
                {
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
            title: "Features of Electronic Platform or Application for Consultation",
            questions: [
                {
                    type: "comment",
                    name: "features",
                    title: "What features would this electronic platform or application for consultation should have ?"
                }
            ]
        }, {
            title: "Example of Matrix",
            questions: [
                {
                    type: "matrix",
                    name: "matrixExample",
                    title: "Example matrix selection for multiple rows.",
                    //visibleIf: "{skinNumber} = 'many' and {skinShips} = 'all'",
                    columns: [
                        "First Column"
                    ],
                    rows: [
                        "Example of row 1"
                    ]
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
                    title: 'Oops !!! Something went wrong.',
                    text: data.OK,
                    type: 'error'
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