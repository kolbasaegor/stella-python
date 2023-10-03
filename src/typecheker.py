from stella.stellaParser import stellaParser
from stypes import *


TYPE_BOOL = Bool()
TYPE_NAT = Nat()
TYPE_UNIT = Unit()
TYPE_ANY = Any()
TYPE_PANIC = Panic()


class Typecheker():

    def __init__(self):
        self.global_functions = dict()


    def type_of_match(self, ctx: stellaParser.MatchContext, local):
        '''
        evaluates type of t0 in match t0 {...}
        returns type of t0
        '''
        s = ctx.getText()
        var = s[:s.find('(')][:s.find('{')].replace('match', '')

        if var in self.global_functions:
            return self.global_functions[var].return_type

        if var in local:
            return local[var]
        
        raise RuntimeError(f'Unknown variable/function "{var}"')


    def handle_type(self, ctx):
        '''
        evaluates type of parameter
        returns type of parameter
        '''
        if isinstance(ctx, stellaParser.TypeUnitContext):
            return TYPE_UNIT

        if isinstance(ctx, stellaParser.TypeBoolContext):
            return TYPE_BOOL
        
        if isinstance(ctx, stellaParser.TypeNatContext):
            return TYPE_NAT
        
        if isinstance(ctx, stellaParser.TypeRefContext):
            return Ref(self.handle_type(ctx.type_))
        
        if isinstance(ctx, stellaParser.TypeFunContext):
            return Fun(
                param_type=self.handle_type(ctx.paramTypes[0]),
                return_type=self.handle_type(ctx.returnType)
            )
        
        if isinstance(ctx, stellaParser.TypeSumContext):
            return Sum(
                left=self.handle_type(ctx.left),
                right=self.handle_type(ctx.right)
            )

        if isinstance(ctx, stellaParser.TypeTupleContext):
            return Tuple([self.handle_type(term) for term in ctx.types])
        
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
            local = dict()
            func_name = ctx.name.text
            param_name = ctx.paramDecls[0].name.text
            param_type = self.handle_type(ctx.paramDecls[0].paramType)
            expected_return_type = self.handle_type(ctx.returnType)
            actual_return_type = None

            self.global_functions[func_name] = Fun(param_type, expected_return_type)
            local[param_name] = param_type
        
            actual_return_type = self.handle_expr_context(ctx.returnExpr, local)
            if not compare_types(expected_return_type, actual_return_type):
                raise RuntimeError(f'Ill-typed function {func_name}: expected return type: {expected_return_type}, actual: {actual_return_type}')

        elif isinstance(ctx, stellaParser.DeclTypeAliasContext):
            raise RuntimeError("Unsupported syntax")
        
        else:
            raise RuntimeError("Unsupported syntax")
        

    def handle_expr_context(self,
                            ctx: stellaParser.ExprContext,
                            local):
        '''
        evaluates expression type
        
        supported expression types:
        ConstTrueContext, ConstFalseContext, VarContext,
        IfContext, ConstIntContext, SuccContext,
        ApplicationContext, AbstractionContext, NatRecContext,
        ConstUnitContext, TupleContext, DotTupleContext,
        InlContext, InrContext, MatchContext, MatchCaseContext,
        PatternInlContext, PatternInrContext, PatternVarContext

        otherwise returns RuntimeError
        '''
        if isinstance(ctx, stellaParser.ConstTrueContext):
            return TYPE_BOOL

        if isinstance(ctx, stellaParser.ConstFalseContext):
            return TYPE_BOOL
        
        if isinstance(ctx, stellaParser.ConstIntContext):
            return TYPE_NAT
        
        if isinstance(ctx, stellaParser.ConstUnitContext):
            return TYPE_UNIT
        
        if isinstance(ctx, stellaParser.PanicContext):
            return TYPE_PANIC
        
        if isinstance(ctx, stellaParser.LetContext):
            let_locals = [self.handle_expr_context(pattern, local) for pattern in ctx.patternBindings]
            for ll in let_locals:
                local = local | ll

            return self.handle_expr_context(ctx.body, local)

        if isinstance(ctx, stellaParser.PatternBindingContext):
            if not isinstance(ctx.pat, stellaParser.PatternVarContext):
                raise RuntimeError(f'{ctx.pat.getText()} is not variable')
            
            return { f'{ctx.pat.name.text}' : self.handle_expr_context(ctx.rhs, local) }

        if isinstance(ctx, stellaParser.SequenceContext):
            self.handle_expr_context(ctx.expr1, local)

            return self.handle_expr_context(ctx.expr2, local)
        
        if isinstance(ctx, stellaParser.RefContext):
            expr_type = self.handle_expr_context(ctx.expr_, local)

            return Ref(expr_type)

        if isinstance(ctx, stellaParser.DerefContext):
            ref = self.handle_expr_context(ctx.expr_, local)

            if not isinstance(ref, Ref):
                raise RuntimeError('Dereferncing non reference object')
            
            return ref.type

        if isinstance(ctx, stellaParser.AssignContext):
            ref = self.handle_expr_context(ctx.lhs, local)
            if not isinstance(ref, Ref):
                raise RuntimeError(f'Reference object has type {ref}, expected: &')

            value_type = self.handle_expr_context(ctx.rhs, local)
            if not compare_types(ref.type, value_type):
                raise RuntimeError(f'Ill-typed assignment: reference object points to type {ref.type}, but assignment value has type {value_type}')

            return TYPE_UNIT

        if isinstance(ctx, stellaParser.InlContext):
            return Sum(
                left=self.handle_expr_context(ctx.expr_, local),
                right=TYPE_ANY
            )
        
        if isinstance(ctx, stellaParser.InrContext):
            return Sum(
                left=TYPE_ANY,
                right=self.handle_expr_context(ctx.expr_, local)
            )

        if isinstance(ctx, stellaParser.MatchContext):
            match_type = self.type_of_match(ctx, local)
            local['inl_pattern'] = match_type.left
            local['inr_pattern'] = match_type.right

            case1_type = self.handle_expr_context(ctx.cases[0], local)
            case2_type = self.handle_expr_context(ctx.cases[1], local)

            if not compare_types(case1_type, case2_type):
                raise RuntimeError(f'Ill-typed mactch: type of case 1 ({case1_type}) != type of case 2 ({case2_type})')

            return case1_type 

        if isinstance(ctx, stellaParser.MatchCaseContext):
            pname, ptype = self.handle_expr_context(ctx.pattern_, local)
            local[pname] = ptype

            return self.handle_expr_context(ctx.expr_, local)

        if isinstance(ctx, stellaParser.PatternInlContext):
            pattern_type = local['inl_pattern']
            pattern_name = self.handle_expr_context(ctx.pattern_, local)

            return pattern_name, pattern_type
        
        if isinstance(ctx, stellaParser.PatternInrContext):
            pattern_type = local['inr_pattern']
            pattern_name = self.handle_expr_context(ctx.pattern_, local)

            return pattern_name, pattern_type

        if isinstance(ctx, stellaParser.PatternVarContext):
            return ctx.name.text

        if isinstance(ctx, stellaParser.TupleContext):
            return Tuple([self.handle_expr_context(expr, local) for expr in ctx.exprs])

        if isinstance(ctx, stellaParser.DotTupleContext):
            tuple_instance = self.handle_expr_context(ctx.expr_, local)
            index = int(ctx.index.text)

            if not isinstance(tuple_instance, Tuple):
                raise RuntimeError(f'Index applied to a non-tuple: {tuple_instance}')
            
            return tuple_instance[index]

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
                raise RuntimeError(f'Ill-typed if statement: expected condition type: Bool, acttual condition type: {condition_type}')

            then_expr_type = self.handle_expr_context(ctx.thenExpr, local)
            else_expr_type = self.handle_expr_context(ctx.elseExpr, local)

            if not compare_types(then_expr_type, else_expr_type):
                raise RuntimeError(f'Ill-typed if statement: thenExprType({then_expr_type}) != elseExprType({else_expr_type})')
            
            return then_expr_type
        
        if isinstance(ctx, stellaParser.SuccContext):
            param_type = self.handle_expr_context(ctx.n, local)
            if not compare_types(TYPE_NAT, param_type):
                raise RuntimeError(f'Ill-typed succ: expected param type: Nat, actual param type: {param_type}')

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
                raise RuntimeError(f'Ill-typed Nat::rec: n should have type Nat, actual type: {n_type}')
            
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

        raise RuntimeError(f'Unsupported syntax: {ctx.getText()}')
    