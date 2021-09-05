import smartpy as sp
import time

# declare the contract
class ScrillaBook(sp.Contract):
    def __init__(self,e,a,s):
        #initialize the smart conract with storage
        mymap = {
            sp.address("tz1Zpr7G56q22MDhceAWSxmQpPm2m93H6rC4"): sp.record(
                date = sp.timestamp(int(time.time())),
                author = a,
                entry = e,
                stake = sp.mutez(s)
                )
        }
    
        self.init(
                mymap = mymap, 
                last= sp.address("tz1Zpr7G56q22MDhceAWSxmQpPm2m93H6rC4")
                )

    #contract entry point to change data
    @sp.entry_point
    def add_entry(self, params):
        last_stake = self.data.mymap[self.data.last].stake
        sp.verify(last_stake < sp.amount, message="send more!")
    
        with sp.if_(self.data.mymap.contains(sp.sender)):
            self.data.mymap[sp.sender].date = sp.now
            self.data.mymap[sp.sender].author = params.a
            self.data.mymap[sp.sender].entry = params.e
            self.data.mymap[sp.sender].stake += sp.amount

        with sp.else_():
            self.data.mymap[sp.sender] = sp.record(
                        date = sp.now,
                        entry = params.e,
                        author = params.a,
                        stake = sp.amount
            )
        self.data.last = sp.sender


    @sp.entry_point
    # withdraw functionality
    def withdraw(self):
        sp.verify( self.data.mymap.contains(sp.sender) ,message="get in first!") 
        amount = self.data.mymap[sp.sender].stake
        sp.verify(amount > sp.mutez(100), message="not enough stake!")
        sp.transfer(sp.unit, amount, sp.contract(sp.TUnit, sp.sender).open_some(message = "error sending"))
        self.data.mymap[sp.sender].stake = sp.mutez(0) 
        

#  Tests to ensure this was done properly
@sp.add_test(name = "ScrillaBook")
def test1():
    scenario = sp.test_scenario()
    scenario.h1("Welcome to ScrillaBook")
    
    initial_balance = sp.mutez(1)
    c1 = ScrillaBook("hello world","ADMIN",1)
    c1.set_initial_balance(initial_balance)
    scenario += c1

    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    charles = sp.test_account("charles")

    scenario += c1.add_entry(a="alice", e = 'hello from alice').run(
                                                            sender = alice,
                                                            amount = sp.tez(2)
                                                            )
                                    
    scenario += c1.add_entry(a="bob",  e = 'hello from bob').run(
                                                                sender = bob,
                                                                amount = sp.tez(3)
                                                                )
    scenario += c1.add_entry(a="charles", e = 'hello from charles').run(
                                                                    sender = charles,
                                                                    amount = sp.tez(15)
                                                                    )
    scenario += c1.withdraw().run(
                                sender = bob,
                                amount = sp.tez(0)
                                )

    scenario += c1.withdraw().run(
                                sender = alice,
                                amount = sp.tez(0)
                                )
sp.add_compilation_target("compd",ScrillaBook("hello world","ADMIN",100))