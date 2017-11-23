import os.path
from .models import ExpectedResult

def read_expected_result(local_output_folder, item):
    # The result is written in result.txt
    output_result = os.path.join(local_output_folder, 'result.txt')
    with open(output_result) as f:
        content = f.readlines()
    content = [x.strip() for x in content] 
    result = [x.split(",") for x in content]
    expected_results = ExpectedResult.objects.filter(image_sheet=item)
    # Render the HTML template index.html with the data in the context variable
    er = []
    for i in range(0,60):
        er.append({})
    for expected_result in expected_results:
        r = int(expected_result.order) - 1
        er[int(expected_result.order) - 1] = [
            expected_result.num,
            expected_result.big,
            expected_result.small,
            expected_result.roll,
            expected_result.is_delete,
        ]
    return (result,er)