from stella.stellaParser import stellaParser
from stypes import Bool, Nat, Fun, compare_types


TYPE_BOOL = Bool()
TYPE_NAT = Nat()


class Typecheker():

    def __init__(self):
        self.global_functions: dict[str, Bool|Nat|Fun] = dict()


    def handle_type(self, ctx):
        if isinstance(ctx, stellaParser.TypeBoolContext):
            return TYPE_BOOL
        
        if isinstance(ctx, stellaParser.TypeNatContext):
            return TYPE_NAT
        
        if isinstance(ctx, stellaParser.TypeFunContext):
            return Fun(
                param_type=self.handle_type(ctx.paramTypes[0]),
                return_type=self.handle_type(ctx.returnType)
            )
        
        if isinstance(ctx, stellaParser.TypeParensContext):
            return self.handle_type(ctx.type_)
        
        raise RuntimeError(f'Unknown type: {type(ctx)}')
        
            
    def handle_program_context(self, ctx: stellaParser.ProgramContext):
        '''
        goes through all function declarations
        returns 0 if all function decls well typed
        '''
        for decl in ctx.decls:
            self.handle_decl_context(decl)

        return 0
        

    def handle_decl_context(self, ctx: stellaParser.DeclContext):
        '''
        typechecks function definition;
        creates dictionary for local variables/functions inside function;
        adds function to the global scope;

        if expected return type != actual return type raises RuntimeError 
        '''
        if isinstance(ctx, stellaParser.DeclFunContext):
            local: dict[str, Bool|Nat|Fun] = dict()
            func_name = ctx.name.text
            param_name = ctx.paramDecls[0].name.text
            param_type = self.handle_type(ctx.paramDecls[0].paramType)
            expected_return_type = self.handle_type(ctx.returnType)
            actual_return_type = None

            self.global_functions[func_name] = Fun(param_type, expected_return_type)
            local[param_name] = param_type
        
            if isinstance(ctx.returnExpr, stellaParser.SequenceContext):
                raise RuntimeError('Do not use ; after the return. Sequencing has not yet been added to this version of typechecker')
            else:
                actual_return_type = self.handle_expr_context(ctx.returnExpr, local)

            if not compare_types(expected_return_type, actual_return_type):
                raise RuntimeError(f'Ill-typed function {func_name}: expected return type: {expected_return_type}, actual: {actual_return_type}')

        elif isinstance(ctx, stellaParser.DeclTypeAliasContext):
            raise RuntimeError("unsupported syntax")
        
        else:
            raise RuntimeError("unsupported syntax")
        

    def handle_expr_context(self,
                            ctx: stellaParser.ExprContext,
                            local: dict[str, Bool|Nat|Fun]):
        '''
        evaluates expression type
        
        supported expression types:
        ConstTrueContext, ConstFalseContext, VarContext,
        IfContext, ConstIntContext, SuccContext,
        ApplicationContext, AbstractionContext, NatRecContext

        otherwise returns RuntimeError
        '''
        if isinstance(ctx, stellaParser.ConstTrueContext):
            return TYPE_BOOL

        elif isinstance(ctx, stellaParser.ConstFalseContext):
            return TYPE_BOOL
        
        elif isinstance(ctx, stellaParser.ConstIntContext):
            return TYPE_NAT

        if isinstance(ctx, stellaParser.VarContext):
            var_name = ctx.name.text 

            if var_name in local:
                return local[var_name]
            
            elif var_name in self.global_functions:
                return self.global_functions[var_name]
            
            raise RuntimeError(f'Unknown variable/function "{ctx.name.text}"')

        if isinstance(ctx, stellaParser.IfContext):
            condition_type = self.handle_expr_context(ctx.condition, local)
            if not compare_types(TYPE_BOOL, condition_type):
                raise RuntimeError(f'Ill-typed if statement: expected condition type: <Bool>, acttual condition type: {condition_type}')

            then_expr_type = self.handle_expr_context(ctx.thenExpr, local)
            else_expr_type = self.handle_expr_context(ctx.elseExpr, local)

            if not compare_types(then_expr_type, else_expr_type):
                raise RuntimeError(f'Ill-typed if statement: thenExprType({then_expr_type}) != elseExprType({else_expr_type})')
            
            return then_expr_type
        
        if isinstance(ctx, stellaParser.SuccContext):
            param_type = self.handle_expr_context(ctx.n, local)
            if not compare_types(TYPE_NAT, param_type):
                raise RuntimeError(f'Ill-typed succ: expected param type: <Nat>, actual param type: {param_type}')

            return TYPE_NAT
                    
        if isinstance(ctx, stellaParser.AbstractionContext):
            param_type = self.handle_type(ctx.paramDecls[0].paramType)
            local[ctx.paramDecls[0].name.text] = param_type

            return Fun(
                param_type=param_type,
                return_type=self.handle_expr_context(ctx.returnExpr, local)
            )

        if isinstance(ctx, stellaParser.NatRecContext):
            n_type = self.handle_expr_context(ctx.n, local)
            if not compare_types(TYPE_NAT, n_type):
                raise RuntimeError(f'Ill-typed Nat::rec: n should have type <Nat>, actual type: {n_type}')
            
            initial_type = self.handle_expr_context(ctx.initial, local)
            step_type = self.handle_expr_context(ctx.step, local)

            if not compare_types(Fun(TYPE_NAT, Fun(initial_type, initial_type)), step_type):
                raise RuntimeError(f'Ill-typed Nat::rec,\nz have type {initial_type};\ns has to be of type (fn(Nat)->(fn({initial_type})->{initial_type}))\nactual type of s: {step_type}')

            return initial_type
        
        if isinstance(ctx, stellaParser.ApplicationContext):
            param_type = self.handle_expr_context(ctx.args[0], local)
            func = self.handle_expr_context(ctx.fun, local)

            if not isinstance(func, Fun):
                raise RuntimeError(f'Applying non function')
            
            if not compare_types(func.param_type, param_type):
                raise RuntimeError(f'Ill-typed application of function {ctx.fun.getText()}: expected param type: {func.param_type}, actual: {param_type}')
            
            return func.return_type
        
        if isinstance(ctx, stellaParser.ParenthesisedExprContext):
            return self.handle_expr_context(ctx.expr_, local)

        raise RuntimeError(f'unsupported syntax: {ctx.getText()}')
        