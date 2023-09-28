from stella.stellaParser import stellaParser


class Typecheker():

    def __init__(self):
        self.fun_decls = {}


    def compare_types(self, expected: str, actual: str):
        '''
        compares two types represented as a string
        '''
        return expected.replace(' ', '') == actual.replace(' ', '')
            

    def handle_program_context(self, ctx: stellaParser.ProgramContext):
        '''
        goes through all function declarations
        '''
        for decl in ctx.decls:
            self.handle_decl_context(decl)

        return 0
        

    def handle_decl_context(self, ctx: stellaParser.DeclContext):
        '''
        typechecks function definition;
        creates a dictionary for local variables inside a function;
        adds a function to the global scope;

        if expected return type != actual return type raises RuntimeError 
        '''
        if isinstance(ctx, stellaParser.DeclFunContext):
            param_type = ctx.paramDecls[0].paramType.getText()
            return_type = ctx.returnType.getText()

            local_variables = {
                f'{ctx.paramDecls[0].name.text}': {
                    'type': ctx.paramDecls[0].paramType.getText()
                }
            }

            self.fun_decls[ctx.name.text] = {
                'param_type': param_type,
                'return_type': return_type
            }

            return_expr_type = self.handle_expr_context(ctx.returnExpr.expr1,
                                                        local_variables=local_variables)
            
            print(f'Function declaration: {ctx.name.text}')
            print(f'- Actual return type: {return_expr_type}')
            print(f'- Expected return type: {return_type}', end='\n\n')

            if not self.compare_types(return_type, return_expr_type):
                raise RuntimeError(f'Type mismatch in function declaration "{ctx.name.text}": \
                                    expected return type: "{return_type}", \
                                    actual return type: "{return_expr_type}"')

        elif isinstance(ctx, stellaParser.DeclTypeAliasContext):
            raise RuntimeError("unsupported syntax")
        
        else:
            raise RuntimeError("unsupported syntax")
        

    def handle_expr_context(self,
                            ctx: stellaParser.ExprContext,
                            local_variables: dict[str, dict[str, str]]):
        '''
        evaluates expression type
        
        supported expression types:
        ConstTrueContext, ConstFalseContext, VarContext,
        IfContext, ConstIntContext, SuccContext,
        ApplicationContext, AbstractionContext, NatRecContext

        otherwise returns RuntimeError
        '''
        if isinstance(ctx, stellaParser.ConstTrueContext):
            return 'Bool'

        elif isinstance(ctx, stellaParser.ConstFalseContext):
            return 'Bool'
        
        elif isinstance(ctx, stellaParser.VarContext):
            if ctx.name.text not in local_variables:
                raise RuntimeError(f'Unknown variable "{ctx.name.text}"')
            
            return local_variables[ctx.name.text]['type']

        elif isinstance(ctx, stellaParser.IfContext):
            condition_type = self.handle_expr_context(ctx.condition, local_variables)
            if not self.compare_types('Bool', condition_type):
                raise RuntimeError(f'Ill-typed if statement: expected condition type: \
                                   "Bool", acttual condition type: "{condition_type}"')

            thenExpr_type = self.handle_expr_context(ctx.thenExpr, local_variables)
            elseExpr_type = self.handle_expr_context(ctx.elseExpr, local_variables)

            if thenExpr_type != elseExpr_type:
                raise RuntimeError(f'Ill-typed if statement: \
                                   thenExprType({thenExpr_type}) != elseExprType({elseExpr_type})')
            
            return thenExpr_type
        
        elif isinstance(ctx, stellaParser.ConstIntContext):
            return 'Nat'
        
        elif isinstance(ctx, stellaParser.SuccContext):
            param_type = self.handle_expr_context(ctx.n, local_variables)
            if not self.compare_types('Nat', param_type):
                raise RuntimeError(f'Ill-typed succ: expected param type: \
                                   "Nat", actual param type: "{param_type}"')

            return 'Nat'
        
        elif isinstance(ctx, stellaParser.ApplicationContext):
            if isinstance(ctx.fun, stellaParser.ApplicationContext):
                return self.handle_expr_context(ctx.args[0], local_variables)

            fun_name = ctx.fun.name.text
            actual_param_type = self.handle_expr_context(ctx._expr, local_variables)

            expected_param_type = self.fun_decls[fun_name]['param_type']

            if not self.compare_types(expected_param_type, actual_param_type):
                raise RuntimeError(f'Type mismatch in function application "{fun_name}": \
                                   expected param type: "{expected_param_type}", actual param type: "{actual_param_type}"')

            return self.fun_decls[fun_name]['return_type']
        
        elif isinstance(ctx, stellaParser.AbstractionContext):
            local_variables[ctx._paramDecl.name.text] = {
                'type': ctx._paramDecl.paramType.getText()
            }
            return_expr_type = self.handle_expr_context(ctx.returnExpr.expr1, local_variables)

            return f'(fn({ctx._paramDecl.paramType.getText()})->{return_expr_type})'

        elif isinstance(ctx, stellaParser.NatRecContext):
            n_type = self.handle_expr_context(ctx.n, local_variables)
            if not self.compare_types('Nat', n_type):
                raise RuntimeError(f'Ill-typed Nat::rec: "n" should have type "Nat", \
                                   actual type: {n_type}')
            
            initial_type = self.handle_expr_context(ctx.initial, local_variables)
            step_type = self.handle_expr_context(ctx.step, local_variables)

            if not self.compare_types(f'(fn(Nat)->(fn({initial_type})->{initial_type}))', step_type):
                raise RuntimeError(f'Ill-typed Nat::rec,\nz have type {initial_type};\
                                   \ns has to be of type (fn(Nat)->(fn({initial_type})->{initial_type}))\
                                   \nactual type of s: {step_type}')

            return 'Nat'
        
        else:
            raise RuntimeError("unsupported syntax")
        