import schurtransform
from schurtransform.transform import SchurTransform, SummaryType

def test_transform_norms():
    samples = [
        [[4,2], [4.01,2.1], [3.9,2.2]],
        [[3.99,2.1], [3.7,2.1] ,[4.0,2.2]],
        [[4.4,1.9], [4.3,1.8], [4.3,1.8]],
        [[4.6,2.0], [4.1,1.8], [4.3,1.7]],
        [[3.6,2.1], [4.5,2], [5,1]],
        [[3.0,2.2], [7,2.2], [5.6,1.2]],
    ]
    st = SchurTransform()
    norms = st.transform(
        samples=samples,
        summary_type=SummaryType.NORMS,
    )
    print(norms)


if __name__=='__main__':
    test_transform_norms()
