__kernel void vector_square(__global float4* input,  __global float4* output) {
  int i = get_global_id(0);
  output[i] = input[i]*input[i];
}
