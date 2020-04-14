str_with_space = ' import_source.h   ATen/core/qualified_name.h   torch/csrc/jit/export.h   ' \
                 'torch/csrc/jit/script/parser.h   torch/csrc/jit/script/resolver.h   ' \
                 'torch/csrc/jit/script/script_type_parser.h  '

no_space_list = str_with_space.split()
print(no_space_list)
one_space_str = ' '.join(no_space_list)
print(one_space_str)
