"""
A summarizer based on the algorithm found in Classifier4J by Nick Lothan.      
In order to summarize a document this algorithm first determines the 
frequencies of the words in the document.  It then splits the document
into a series of sentences.  Then it creates a summary by including the
first sentence that includes each of the most frequent words.  Finally
summary's sentences are reordered to reflect that of those in the original 
document.
"""

##//////////////////////////////////////////////////////
##  Simple Summarizer
##//////////////////////////////////////////////////////

from nltk.probability import FreqDist 
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk.data
import time

input = """

The White House openly criticised Russia for giving Edward Snowden a "propaganda platform" on Friday, after the whistleblower was permitted to meet human rights activists in the Moscow airport where he has been trapped for three weeks.
Hours before Barack Obama was due to speak with Vladimir Putin on the telephone, senior US officials publicly chided Moscow for facilitating the high-profile event.

Snowden, a former contractor who leaked classified National Security Agency information about US surveillance tactics, has been trapped in a Sheremetyevo airport since arriving from Hong Kong on 23 June.

In his first public appearance since identifying himself as the source of the leaks last month, Snowden met human rights lawyers and announced that he intends to renew an earlier request for asylum in Russia, although in the longer term he said he will seek safe passage to Latin America.

Those present at the Moscow event said it must have been sanctioned or even choreographed by Russian officials; airport employees organised and conducted the event, and order was kept by a small cadre of policemen.

In Washington, Obama's press secretary Jay Carney said the president would discuss Snowden's case with Putin during a scheduled phone call. "I would simply say that providing a propaganda platform for Mr Snowden runs counter to the Russian government's previous declarations of Russia's neutrality, and that they have no control over his presence in the airport," he said.

"It is also incompatible with Russian assurances that they do not want Mr Snowden to further damage US interests."

He added: "We don't believe this should - and we don't want it to - do harm to our important relationship with Russia. We continue to discuss with Russia our strongly held view that there is absolute legal justification for him to be expelled, for him to be returned to the United States to face the charges that have been brought against him for the unauthorised leaking of classified information."

Asked about the involvement of Amnesty International and Human Rights Watch, both of which sent representatives to meet Snowden, Carney replied: "Those groups do important work. But Mr Snowden is not a human rights activist or a dissident. He is accused of leaking classified information, has been charged with three felony counts, and should be returned to the United States, where he will be afforded full due process."

In comments unlikely to smooth diplomatic relations, he said the Russian government should permit human rights groups to do their work "throughout Russia, not just at the Moscow [airport] transit lounge".

The White House would not be drawn on the likely content of Obama's phone call with Putin, but it seems inconceivable that the plight of the former NSA contractor will not be the subject of a difficult conversation.

Putin's spokesman repeated the Russian president's previous declaration that Snowden should stop harming the interests of the US if he wants asylum. But in a sign that Moscow may be inclined to grant Snowden safe haven, Vyacheslav Nikonov, a pro-Kremlin lawmaker who attended the airport meeting, said the former spy appeared to be willing to meet that condition.

At the Moscow airport meeting, Snowden said the US was undertaking "unlawful" attempts to prevent his arrival to countries in which he has been granted asylum. In a statement read at the meeting and released later by WikiLeaks, he described his decision to leak secret NSA documents to the Guardian and Washington Post as a "moral decision".

"I did what I believed right," he said. "I did not seek to enrich myself. I did not seek to sell US secrets. I did not partner with any foreign government to guarantee my safety. Instead, I took what I knew to the public, so what affects all of us can be discussed by all of us in the light of day, and I asked the world for justice."

Despite Obama having claimed publicly that the US does not intend to expend much energy in securing the extradition of a "a 29-year-old hacker", the reality is that senior officials have been lobbying hard behind the scenes, particularly in Latin America, where three countries - Venezuela, Nicaragua and Bolivia - have offered to grant Snowden asylum.

Vice-president Joe Biden is known to have been instrumental in persuading Ecuadorean president Rafael Correa not to offer asylum to Snowden.

The US is also widely believed to have been behind the decision by European countries to block a plane carrying the Bolivian president, Evo Morales, from traveling through their airspace amid suspicions that Snowden was on board.
On Friday, a senior State Department official told the New York Times that countries throughout Latin America had been made aware of the repercussions of granting asylum to Snowden.

Relations with any country seen to be helping the former NSA contractor would be "in a very bad place for a long time to come", the official said.

At a State Department press conference, chief spokesperson Jen Psaki said the US was disappointed that Russia appeared to have facilitated Snowden's high-profile meeting with human rights activists.

Echoing the language used by the White House, she said: "Our concern here is [Snowden] has been provided this opportunity to speak in a propaganda platform, that Russia has played a role in facilitating this, that others have helped elevate this," she said.

She said that Moscow's handling of the case risked damaging its relationship with the US, but added: "we are not at this point yet".

Psaki said that Russia "still has the opportunity to do the right thing and help return Mr Snowden to the US".

"""

keys = ['Snowden',  'Moscow',  'Russia',  'airport',  'rights',  'asylum',  'Russian',  'Putin',
'meeting',  'Obama',  'president',  'day',  'countries',  'email',  'news',  'Mr',  'Guardian',  'NSA',
'editors',  'contractor',  'government',  'activists',  'officials',  'event',  'decision' ]

class SimpleSummarizer:
    def __init__(self):
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.tokenizer = RegexpTokenizer('\w+')

    def reorder_sentences( self, output_sentences, input ):
        output_sentences.sort( lambda s1, s2:
            input.find(s1) - input.find(s2) )
        return output_sentences

    def keyword_summarize(self, keys, input, num_sentences):
        '''iterate over the most keywords, and add the first sentence
        that includes each word to the result. actual_sentences are the literal
        sentences, working is all lowercased for comparisons. Then sort
        the sentences back to original order'''
        actual_sentences = self.sent_detector.tokenize(input)
        working_sentences = [sentence.lower()
            for sentence in actual_sentences]

        output_sentences = []
        if len(working_sentences) < 1: return ""

        output_sentences.append(actual_sentences[0])

        if len(working_sentences) > 1:
            for word in keys:
                for i in range(1, len(working_sentences)):
                    if (word.lower() in working_sentences[i]
                      and actual_sentences[i] not in output_sentences):
                        output_sentences.append(actual_sentences[i])
                        break
                    if len(output_sentences) >= num_sentences-1: break
                if len(output_sentences) >= num_sentences-1: break

            output_sentences = self.reorder_sentences(output_sentences, input)

        return "  ".join(output_sentences)

    def summarize(self, input, num_sentences ):
        # TODO: allow the caller to specify the tokenizer they want
        # TODO: allow the user to specify the sentence tokenizer they want
        # get the frequency of each word in the input
        base_words = [word.lower()
            for word in self.tokenizer.tokenize(input)]
        words = [word for word in base_words if word not in stopwords.words()]
        word_frequencies = FreqDist(words)

        # now create a set of the most frequent words
        most_frequent_words = [pair[0] for pair in
            word_frequencies.items()[:100]]

        print word_frequencies.items()

        actual_sentences = self.sent_detector.tokenize(input)
        working_sentences = [sentence.lower()
            for sentence in actual_sentences]

        output_sentences = []
        for word in most_frequent_words:
            for i in range(0, len(working_sentences)):
                if (word in working_sentences[i]
                  and actual_sentences[i] not in output_sentences):
                    output_sentences.append(actual_sentences[i])
                    break
                if len(output_sentences) >= num_sentences: break
            if len(output_sentences) >= num_sentences: break

        output_sentences = self.reorder_sentences(output_sentences, input)
        return "  ".join(output_sentences)


if __name__ == '__main__':
    s0=time.time()
    s = SimpleSummarizer()
    print 'initializing took', time.time() - s0, 'seconds'

    s1 = time.time()
    print s.keyword_summarize(keys, input, 5)
    print 'calculating took', time.time() - s1, 'seconds'

    print s.summarize(input, 5)

SUMMARIZER = SimpleSummarizer()
