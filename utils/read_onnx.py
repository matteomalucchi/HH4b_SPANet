import onnxruntime    # to inference ONNX models, we use the ONNX Runtime
import numpy as np
import argparse

arg_parser = argparse.ArgumentParser(description='Read ONNX model')
arg_parser.add_argument('-m', '--model', type=str, help='Path to ONNX model')
args = arg_parser.parse_args()


session = onnxruntime.InferenceSession(
    args.model,
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)

input_name=[input.name for input in session.get_inputs()]
output_name=[output.name for output in session.get_outputs()]
print("Inputs name:", input_name)
print("Outputs name:", output_name)

input_shape=[input.shape for input in session.get_inputs()]
output_shape=[output.shape for output in session.get_outputs()]
print("Inputs shape:", input_shape)
print("Outputs shape:", output_shape)

input_data = [1.]* input_shape[0][2]

input_example = {input_name[0]: [input_data], input_name[1]: np.stack(input_data)[:,:,0]}
output = session.run(output_name, input_example)
print("Output:", output)
